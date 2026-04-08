from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone

from jobs.models import JobPost
from applications.models import Application
from notifications.utils import notify
from notifications.models import Notification
from .models import Assessment, Question, AssessmentAttempt, Answer


def _is_recruiter(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'recruiter'


def _is_job_seeker(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'job_seeker'


# ---------------------------------------------------------------------------
# Recruiter: Create / Edit Assessment for a Job
# ---------------------------------------------------------------------------

@login_required
def manage_assessment(request, job_pk):
    """Recruiter creates or edits the 25-question MCQ for a job."""
    if not _is_recruiter(request.user):
        messages.error(request, "Only recruiters can manage assessments.")
        return redirect('jobs:board')

    job = get_object_or_404(JobPost, pk=job_pk)
    try:
        if job.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('jobs:manage')
    except Exception:
        return redirect('jobs:manage')

    assessment, _ = Assessment.objects.get_or_create(
        job=job,
        defaults={'recruiter': request.user.recruiter_profile, 'title': f'{job.title} Assessment'}
    )

    if request.method == 'POST':
        # Save assessment meta
        assessment.title = request.POST.get('title', assessment.title).strip() or assessment.title
        assessment.instructions = request.POST.get('instructions', '').strip()
        assessment.pass_mark = int(request.POST.get('pass_mark', 20))
        assessment.time_limit_minutes = int(request.POST.get('time_limit_minutes', 30))
        assessment.save()

        # Delete old questions and recreate from POST
        assessment.questions.all().delete()

        texts    = request.POST.getlist('q_text')
        opt_a    = request.POST.getlist('q_option_a')
        opt_b    = request.POST.getlist('q_option_b')
        opt_c    = request.POST.getlist('q_option_c')
        opt_d    = request.POST.getlist('q_option_d')
        correct  = request.POST.getlist('q_correct')

        questions_to_create = []
        for i, text in enumerate(texts):
            text = text.strip()
            if not text:
                continue
            questions_to_create.append(Question(
                assessment=assessment,
                text=text,
                option_a=opt_a[i].strip() if i < len(opt_a) else '',
                option_b=opt_b[i].strip() if i < len(opt_b) else '',
                option_c=opt_c[i].strip() if i < len(opt_c) else '',
                option_d=opt_d[i].strip() if i < len(opt_d) else '',
                correct_option=correct[i] if i < len(correct) else 'A',
                order=i + 1,
            ))
        Question.objects.bulk_create(questions_to_create)

        q_count = len(questions_to_create)
        if q_count == 25:
            messages.success(request, f'Assessment saved with {q_count} questions.')
        elif q_count > 0:
            messages.warning(request, f'Assessment saved with {q_count}/25 questions. Add more to reach 25.')
        else:
            messages.warning(request, 'No questions saved. Please add questions.')

        return redirect('assessment:manage', job_pk=job.pk)

    questions = list(assessment.questions.order_by('order'))
    # Pad to 25 slots for the form
    while len(questions) < 25:
        questions.append(None)

    return render(request, 'assessment/manage.html', {
        'job': job,
        'assessment': assessment,
        'questions': questions,
        'q_range': range(1, 26),
    })


# ---------------------------------------------------------------------------
# Recruiter: Send Assessment to a Shortlisted Applicant
# ---------------------------------------------------------------------------

@login_required
@require_POST
def send_assessment(request, app_pk):
    """Recruiter sends the assessment to a shortlisted applicant."""
    if not _is_recruiter(request.user):
        return redirect('jobs:board')

    app = get_object_or_404(Application, pk=app_pk)

    try:
        if app.job.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('jobs:manage')
    except Exception:
        return redirect('jobs:manage')

    if app.status != Application.STATUS_SHORTLISTED:
        messages.error(request, "You can only send assessments to shortlisted applicants.")
        return redirect('applications:applicants', pk=app.job_id)

    try:
        assessment = app.job.assessment
    except Assessment.DoesNotExist:
        messages.error(request, "No assessment set up for this job. Please create one first.")
        return redirect('assessment:manage', job_pk=app.job_id)

    if assessment.question_count == 0:
        messages.error(request, "Assessment has no questions. Please add questions first.")
        return redirect('assessment:manage', job_pk=app.job_id)

    if hasattr(app, 'assessment_attempt'):
        messages.info(request, "Assessment already sent to this applicant.")
        return redirect('applications:applicants', pk=app.job_id)

    attempt = AssessmentAttempt.objects.create(
        application=app,
        assessment=assessment,
        status=AssessmentAttempt.STATUS_PENDING,
    )

    recruiter_user = request.user
    job_title = app.job.title
    company = app.job.recruiter.company_name

    notify(
        app.applicant,
        Notification.TYPE_ASSESSMENT,
        title=f'Assessment assigned: {job_title}',
        message=f'{company} has sent you an assessment for {job_title}. '
                f'You have {assessment.time_limit_minutes} minutes to complete it.',
        link=f'/assessment/take/{attempt.pk}/',
        from_user=recruiter_user,
    )

    messages.success(request, f'Assessment sent to {app.full_name or app.applicant.email}.')
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and next_url.startswith('/'):
        return redirect(next_url)
    return redirect('applications:applicants', pk=app.job_id)


# ---------------------------------------------------------------------------
# Recruiter: View Attempt Result
# ---------------------------------------------------------------------------

@login_required
def attempt_detail(request, attempt_pk):
    """Recruiter views the seeker's submitted answers and score."""
    if not _is_recruiter(request.user):
        return redirect('jobs:board')

    attempt = get_object_or_404(AssessmentAttempt, pk=attempt_pk)

    try:
        if attempt.assessment.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('jobs:manage')
    except Exception:
        return redirect('jobs:manage')

    answers = attempt.answers.select_related('question').order_by('question__order')
    return render(request, 'assessment/result.html', {
        'attempt': attempt,
        'answers': answers,
        'is_recruiter': True,
    })


# ---------------------------------------------------------------------------
# Job Seeker: Take Assessment
# ---------------------------------------------------------------------------

@login_required
def take_assessment(request, attempt_pk):
    """Job seeker takes the quiz."""
    if not _is_job_seeker(request.user):
        return redirect('jobs:board')

    attempt = get_object_or_404(
        AssessmentAttempt,
        pk=attempt_pk,
        application__applicant=request.user,
    )

    if attempt.status in (AssessmentAttempt.STATUS_PASSED, AssessmentAttempt.STATUS_FAILED):
        return redirect('assessment:my_result', attempt_pk=attempt.pk)

    questions = attempt.assessment.questions.order_by('order')

    if request.method == 'POST':
        # Mark as started if not already
        if not attempt.started_at:
            attempt.started_at = timezone.now()

        attempt.answers.all().delete()
        score = 0
        answers_to_create = []
        for q in questions:
            selected = request.POST.get(f'q_{q.pk}', '').strip().upper()
            if selected not in ('A', 'B', 'C', 'D'):
                selected = ''
            is_correct = selected == q.correct_option
            if is_correct:
                score += 1
            answers_to_create.append(Answer(
                attempt=attempt,
                question=q,
                selected_option=selected,
                is_correct=is_correct,
            ))
        Answer.objects.bulk_create(answers_to_create)

        attempt.score = score
        attempt.completed_at = timezone.now()
        pass_mark = attempt.assessment.pass_mark
        recruiter_user = attempt.assessment.recruiter.user
        job_title = attempt.application.job.title

        if score >= pass_mark:
            attempt.status = AssessmentAttempt.STATUS_PASSED
            attempt.save()
            notify(
                request.user,
                Notification.TYPE_ASSESSMENT_PASSED,
                title=f'You passed the assessment for {job_title}!',
                message=f'Congratulations! You scored {score}/{attempt.total_questions} and are advancing to the next round.',
                link=f'/assessment/my-result/{attempt.pk}/',
                from_user=recruiter_user,
            )
        else:
            attempt.status = AssessmentAttempt.STATUS_FAILED
            attempt.save()
            notify(
                request.user,
                Notification.TYPE_ASSESSMENT_FAILED,
                title=f'Assessment result: {job_title}',
                message=f'You scored {score}/{attempt.total_questions}. A minimum of {pass_mark} is required to proceed.',
                link=f'/assessment/my-result/{attempt.pk}/',
                from_user=recruiter_user,
            )

        # Notify recruiter
        seeker_name = request.user.get_full_name() or request.user.email
        notify(
            recruiter_user,
            Notification.TYPE_ASSESSMENT_DONE,
            title=f'{seeker_name} completed the assessment',
            message=f'{seeker_name} scored {score}/{attempt.total_questions} on the {job_title} assessment.',
            link=f'/assessment/result/{attempt.pk}/',
            from_user=request.user,
        )

        return redirect('assessment:my_result', attempt_pk=attempt.pk)

    # GET — start timer on first load
    if not attempt.started_at:
        attempt.started_at = timezone.now()
        attempt.status = AssessmentAttempt.STATUS_IN_PROGRESS
        attempt.save(update_fields=['started_at', 'status'])

    # Calculate remaining seconds
    elapsed = (timezone.now() - attempt.started_at).total_seconds()
    total_seconds = attempt.assessment.time_limit_minutes * 60
    remaining_seconds = max(0, int(total_seconds - elapsed))

    return render(request, 'assessment/take.html', {
        'attempt': attempt,
        'questions': questions,
        'remaining_seconds': remaining_seconds,
    })


# ---------------------------------------------------------------------------
# Job Seeker: View Own Result
# ---------------------------------------------------------------------------

@login_required
def attempt_result(request, attempt_pk):
    """Job seeker sees their score after completing the assessment."""
    if not _is_job_seeker(request.user):
        return redirect('jobs:board')

    attempt = get_object_or_404(
        AssessmentAttempt,
        pk=attempt_pk,
        application__applicant=request.user,
    )
    answers = attempt.answers.select_related('question').order_by('question__order')
    return render(request, 'assessment/result.html', {
        'attempt': attempt,
        'answers': answers,
        'is_recruiter': False,
    })
