from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from django.http import FileResponse

from applications.models import Application
from .models import Assessment, Question, AssessmentAttempt, Answer, DocumentSubmission
from notifications.utils import notify
from notifications.models import Notification


def _is_recruiter(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'recruiter'


def _is_job_seeker(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'job_seeker'


# ---------------------------------------------------------------------------
# Recruiter: Create Assessment
# ---------------------------------------------------------------------------

@login_required
def create_assessment(request, application_pk):
    """Recruiter creates a 25-question MCQ assessment for a shortlisted candidate."""
    if not _is_recruiter(request.user):
        messages.error(request, "Only recruiters can create assessments.")
        return redirect('applications:all_applications')

    app = get_object_or_404(Application, pk=application_pk)

    try:
        if app.job.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('applications:all_applications')
    except Exception:
        return redirect('applications:all_applications')

    if app.status != 'shortlisted':
        messages.error(request, "Assessments can only be sent to shortlisted candidates.")
        return redirect('applications:all_applications')

    # Redirect if assessment already sent
    existing = app.assessment_obj
    if existing:
        messages.info(request, "An assessment has already been sent for this application.")
        return redirect('assessments:recruiter_result', pk=existing.pk)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        instructions = request.POST.get('instructions', '').strip()
        try:
            time_limit = max(0, int(request.POST.get('time_limit_mins', 30)))
        except (ValueError, TypeError):
            time_limit = 30

        if not title:
            messages.error(request, "Please provide an assessment title.")
        else:
            # Validate all 25 questions
            questions_data = []
            errors = []
            for i in range(1, 26):
                q_text  = request.POST.get(f'q{i}_text', '').strip()
                opt_a   = request.POST.get(f'q{i}_a', '').strip()
                opt_b   = request.POST.get(f'q{i}_b', '').strip()
                opt_c   = request.POST.get(f'q{i}_c', '').strip()
                opt_d   = request.POST.get(f'q{i}_d', '').strip()
                correct = request.POST.get(f'q{i}_correct', '').strip().lower()

                if not q_text:
                    errors.append(f"Question {i}: Question text is required.")
                elif not (opt_a and opt_b and opt_c and opt_d):
                    errors.append(f"Question {i}: All four options (A–D) are required.")
                elif correct not in ('a', 'b', 'c', 'd'):
                    errors.append(f"Question {i}: Please mark the correct answer.")
                else:
                    questions_data.append({
                        'order': i,
                        'question_text': q_text,
                        'option_a': opt_a,
                        'option_b': opt_b,
                        'option_c': opt_c,
                        'option_d': opt_d,
                        'correct_answer': correct,
                    })

            if errors:
                for err in errors[:4]:
                    messages.error(request, err)
                if len(errors) > 4:
                    messages.error(request, f"… and {len(errors) - 4} more errors. Please fix all questions.")
            else:
                # Save assessment and questions
                assessment = Assessment.objects.create(
                    application=app,
                    title=title,
                    instructions=instructions,
                    time_limit_mins=time_limit,
                    created_by=request.user,
                )
                for qd in questions_data:
                    Question.objects.create(assessment=assessment, **qd)

                # Notify job seeker
                company = app.job.recruiter.company_name
                notify(
                    app.applicant,
                    Notification.TYPE_ASSESSMENT,
                    title=f'Assessment ready: {app.job.title}',
                    message=(
                        f'{company} has sent you a 25-question assessment for '
                        f'{app.job.title}. Please complete it from your Applications dashboard.'
                    ),
                    link='/applications/my-applications/',
                    from_user=request.user,
                )
                messages.success(
                    request,
                    f"Assessment sent to {app.applicant.email}! They'll be notified."
                )
                return redirect('applications:all_applications')

    return render(request, 'assessments/create.html', {
        'app': app,
        'question_range': range(1, 26),
    })


# ---------------------------------------------------------------------------
# Job Seeker: Take Assessment
# ---------------------------------------------------------------------------

@login_required
def take_assessment(request, pk):
    """Job seeker takes an assessment sent by the recruiter."""
    if not _is_job_seeker(request.user):
        messages.error(request, "Only job seekers can take assessments.")
        return redirect('applications:my_applications')

    assessment = get_object_or_404(Assessment, pk=pk)

    if assessment.application.applicant != request.user:
        messages.error(request, "Access denied.")
        return redirect('applications:my_applications')

    # Redirect if already completed
    attempt_obj = assessment.attempt_obj
    if attempt_obj and attempt_obj.is_completed:
        return redirect('assessments:result', pk=attempt_obj.pk)

    questions = assessment.questions.all().order_by('order')

    if request.method == 'POST':
        attempt, _ = AssessmentAttempt.objects.get_or_create(
            assessment=assessment,
            applicant=request.user,
            defaults={'total_count': questions.count()},
        )
        if attempt.is_completed:
            return redirect('assessments:result', pk=attempt.pk)

        correct_count = 0
        answered_count = 0
        for question in questions:
            selected = request.POST.get(f'q_{question.pk}', '').strip().lower()
            if selected in ('a', 'b', 'c', 'd'):
                is_correct = (selected == question.correct_answer)
                Answer.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={'selected_option': selected, 'is_correct': is_correct},
                )
                if is_correct:
                    correct_count += 1
                answered_count += 1

        total = questions.count()
        score = round((correct_count / total * 100), 1) if total > 0 else 0

        attempt.correct_count = correct_count
        attempt.total_count = total
        attempt.score = score
        attempt.is_completed = True
        attempt.completed_at = timezone.now()
        attempt.save()

        # Notify recruiter
        recruiter_user = assessment.application.job.recruiter.user
        applicant_name = request.user.get_full_name() or request.user.email
        notify(
            recruiter_user,
            Notification.TYPE_ASSESSMENT_DONE,
            title=f'Assessment completed: {assessment.application.job.title}',
            message=(
                f'{applicant_name} scored {score}% on the assessment '
                f'for {assessment.application.job.title}.'
            ),
            link=f'/assessments/{assessment.pk}/recruiter-result/',
            from_user=request.user,
        )

        messages.success(request, f"Assessment submitted! Your score: {score}%")
        return redirect('assessments:result', pk=attempt.pk)

    return render(request, 'assessments/take.html', {
        'assessment': assessment,
        'questions': questions,
    })


# ---------------------------------------------------------------------------
# Job Seeker: View Result
# ---------------------------------------------------------------------------

@login_required
def assessment_result(request, pk):
    """Job seeker views their completed assessment result."""
    attempt = get_object_or_404(AssessmentAttempt, pk=pk)

    if attempt.applicant != request.user:
        messages.error(request, "Access denied.")
        return redirect('applications:my_applications')

    answers = attempt.answers.select_related('question').order_by('question__order')
    return render(request, 'assessments/result.html', {
        'attempt': attempt,
        'answers': answers,
    })


# ---------------------------------------------------------------------------
# Recruiter: View Assessment Results
# ---------------------------------------------------------------------------

@login_required
def recruiter_result(request, pk):
    """Recruiter views the assessment and candidate's result."""
    if not _is_recruiter(request.user):
        messages.error(request, "Access denied.")
        return redirect('applications:all_applications')

    assessment = get_object_or_404(Assessment, pk=pk)

    try:
        if assessment.application.job.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('applications:all_applications')
    except Exception:
        return redirect('applications:all_applications')

    attempt = assessment.attempt_obj
    answers = []
    if attempt and attempt.is_completed:
        answers = attempt.answers.select_related('question').order_by('question__order')

    # Has the candidate submitted documents?
    has_docs = attempt and attempt.documents.exists() if attempt else False

    return render(request, 'assessments/recruiter_result.html', {
        'assessment': assessment,
        'attempt': attempt,
        'answers': answers,
        'has_docs': has_docs,
    })


# ---------------------------------------------------------------------------
# Recruiter: Request Document Verification
# ---------------------------------------------------------------------------

@login_required
def request_docs(request, pk):
    """Recruiter requests document verification from a candidate after seeing their result."""
    if not _is_recruiter(request.user):
        messages.error(request, "Access denied.")
        return redirect('applications:all_applications')

    assessment = get_object_or_404(Assessment, pk=pk)

    try:
        if assessment.application.job.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('applications:all_applications')
    except Exception:
        return redirect('applications:all_applications')

    attempt = assessment.attempt_obj
    if not attempt or not attempt.is_completed:
        messages.error(request, "The candidate must complete the assessment before documents can be requested.")
        return redirect('assessments:recruiter_result', pk=pk)

    if assessment.doc_requested:
        messages.info(request, "Document verification has already been requested for this candidate.")
        return redirect('assessments:recruiter_result', pk=pk)

    assessment.doc_requested = True
    assessment.save(update_fields=['doc_requested'])

    # Notify the job seeker
    applicant = assessment.application.applicant
    company = assessment.application.job.recruiter.company_name
    job_title = assessment.application.job.title
    notify(
        applicant,
        Notification.TYPE_DOCS_REQUESTED,
        title=f'Document verification required: {job_title}',
        message=(
            f'{company} has reviewed your assessment and requires document verification '
            f'for your application to {job_title}. Please upload your Work Experience, '
            f'Certificates, and Criminal Record Check from your results page.'
        ),
        link=f'/assessments/result/{attempt.pk}/',
        from_user=request.user,
    )

    messages.success(request, f"Document verification request sent to {applicant.email}.")
    return redirect('assessments:recruiter_result', pk=pk)


# ---------------------------------------------------------------------------
# Document Submission — Step-by-step (Job Seeker)
# ---------------------------------------------------------------------------

STEPS = ['experience', 'certificate', 'criminal']

STEP_META = {
    'experience': {
        'number': 1,
        'label': 'Work Experience',
        'icon': '💼',
        'instructions': (
            'Upload your employment letters, reference letters, or experience certificates. '
            'Accepted formats: PDF, JPG, PNG, DOCX.'
        ),
        'next': 'certificate',
    },
    'certificate': {
        'number': 2,
        'label': 'Certificates',
        'icon': '🎓',
        'instructions': (
            'Upload your educational certificates, professional qualifications, '
            'or course completion certificates. Accepted formats: PDF, JPG, PNG, DOCX.'
        ),
        'next': 'criminal',
    },
    'criminal': {
        'number': 3,
        'label': 'Criminal Record Check',
        'icon': '🔍',
        'instructions': (
            'Upload your police clearance certificate or background check document. '
            'Accepted formats: PDF, JPG, PNG.'
        ),
        'next': None,
    },
}


@login_required
def submit_docs(request, attempt_pk, step):
    """Job seeker submits documents step-by-step after passing the assessment."""
    if not _is_job_seeker(request.user):
        messages.error(request, "Only job seekers can submit documents.")
        return redirect('applications:my_applications')

    attempt = get_object_or_404(AssessmentAttempt, pk=attempt_pk)

    if attempt.applicant != request.user:
        messages.error(request, "Access denied.")
        return redirect('applications:my_applications')

    if not attempt.is_completed:
        messages.error(request, "Please complete the assessment first.")
        return redirect('assessments:result', pk=attempt_pk)

    if not attempt.assessment.doc_requested:
        messages.error(request, "Document submission has not been requested by the recruiter yet.")
        return redirect('assessments:result', pk=attempt_pk)

    if step not in STEP_META:
        return redirect('assessments:submit_docs', attempt_pk=attempt_pk, step='experience')

    meta = STEP_META[step]

    # Which steps are already done?
    done_steps = set(
        DocumentSubmission.objects.filter(attempt=attempt)
        .values_list('document_type', flat=True).distinct()
    )

    if request.method == 'POST':
        files = request.FILES.getlist('files')
        notes = request.POST.get('notes', '').strip()

        if not files:
            messages.error(request, "Please upload at least one file.")
        else:
            for f in files:
                DocumentSubmission.objects.create(
                    attempt=attempt,
                    document_type=step,
                    title=f.name,
                    file=f,
                    notes=notes,
                )

            next_step = meta['next']
            if next_step:
                messages.success(
                    request,
                    f"{meta['label']} uploaded! Now submit your {STEP_META[next_step]['label']}."
                )
                return redirect('assessments:submit_docs', attempt_pk=attempt_pk, step=next_step)
            else:
                # All three steps done — notify recruiter
                recruiter_user = attempt.assessment.application.job.recruiter.user
                applicant_name = request.user.get_full_name() or request.user.email
                notify(
                    recruiter_user,
                    Notification.TYPE_DOCS_SUBMITTED,
                    title=f'Documents submitted: {attempt.assessment.application.job.title}',
                    message=(
                        f'{applicant_name} has submitted all verification documents '
                        f'(experience, certificates, criminal record) for {attempt.assessment.application.job.title}.'
                    ),
                    link=f'/assessments/{attempt_pk}/recruiter-docs/',
                    from_user=request.user,
                )
                messages.success(request, "All documents submitted successfully! The recruiter has been notified.")
                return redirect('assessments:docs_complete', attempt_pk=attempt_pk)

    # Build a flat steps list so the template needs no custom filters
    steps_list = [
        {
            'key':     s,
            'label':   STEP_META[s]['label'],
            'icon':    STEP_META[s]['icon'],
            'number':  STEP_META[s]['number'],
            'done':    s in done_steps,
            'current': s == step,
            'last':    STEP_META[s]['next'] is None,
        }
        for s in STEPS
    ]
    next_step_label = STEP_META[meta['next']]['label'] if meta['next'] else None

    return render(request, 'assessments/submit_docs.html', {
        'attempt':         attempt,
        'step':            step,
        'meta':            meta,
        'steps_list':      steps_list,
        'done_steps':      done_steps,
        'next_step_label': next_step_label,
    })


@login_required
def docs_complete(request, attempt_pk):
    """Completion confirmation after all documents have been submitted."""
    attempt = get_object_or_404(AssessmentAttempt, pk=attempt_pk)

    if attempt.applicant != request.user:
        messages.error(request, "Access denied.")
        return redirect('applications:my_applications')

    docs = attempt.documents.order_by('document_type', 'submitted_at')
    return render(request, 'assessments/docs_complete.html', {
        'attempt': attempt,
        'docs': docs,
    })


# ---------------------------------------------------------------------------
# Document Viewer — Recruiter
# ---------------------------------------------------------------------------

@login_required
def recruiter_docs(request, attempt_pk):
    """Recruiter views all submitted documents for a candidate."""
    if not _is_recruiter(request.user):
        messages.error(request, "Access denied.")
        return redirect('applications:all_applications')

    attempt = get_object_or_404(AssessmentAttempt, pk=attempt_pk)

    try:
        if attempt.assessment.application.job.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('applications:all_applications')
    except Exception:
        return redirect('applications:all_applications')

    # Build a flat, pre-labelled groups list so the template needs no custom filters
    raw = {}
    for doc in attempt.documents.order_by('document_type', 'submitted_at'):
        raw.setdefault(doc.document_type, []).append(doc)

    groups_list = [
        {
            'type':  dt,
            'label': STEP_META.get(dt, {}).get('label', dt.title()),
            'icon':  STEP_META.get(dt, {}).get('icon', '📂'),
            'docs':  docs_in_group,
        }
        for dt, docs_in_group in raw.items()
    ]

    total_files = sum(len(g['docs']) for g in groups_list)

    return render(request, 'assessments/recruiter_docs.html', {
        'attempt':      attempt,
        'groups_list':  groups_list,
        'total_files':  total_files,
    })


@login_required
def download_doc(request, doc_pk):
    """Serve a submitted document to either the applicant or the recruiter."""
    import os
    doc = get_object_or_404(DocumentSubmission, pk=doc_pk)
    attempt = doc.attempt

    # Permission check
    if request.user == attempt.applicant:
        pass
    elif _is_recruiter(request.user):
        try:
            if attempt.assessment.application.job.recruiter != request.user.recruiter_profile:
                messages.error(request, "Access denied.")
                return redirect('applications:all_applications')
        except Exception:
            messages.error(request, "Access denied.")
            return redirect('applications:all_applications')
    else:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')

    return FileResponse(
        doc.file.open('rb'),
        as_attachment=True,
        filename=os.path.basename(doc.file.name),
    )
