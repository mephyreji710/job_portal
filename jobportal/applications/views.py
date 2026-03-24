import mimetypes
import os

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import FileResponse, Http404

from jobs.models import JobPost
from .models import Application
from .forms import ApplyForm
from notifications.utils import notify
from notifications.models import Notification


def _is_job_seeker(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'job_seeker'


def _is_recruiter(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'recruiter'


# ---------------------------------------------------------------------------
# Job Seeker: Apply
# ---------------------------------------------------------------------------

@login_required
def apply(request, pk):
    """Show apply form (GET) or submit application (POST)."""
    if not _is_job_seeker(request.user):
        messages.error(request, "Only job seekers can apply to jobs.")
        return redirect('jobs:detail', pk=pk)

    job = get_object_or_404(JobPost, pk=pk, status='active')

    # Check for existing application
    existing = Application.objects.filter(job=job, applicant=request.user).first()
    if existing:
        messages.info(request, "You have already applied to this job.")
        return redirect('applications:my_applications')

    from resume.models import Resume
    user_resumes = Resume.objects.filter(user=request.user).order_by('-is_primary', '-uploaded_at')

    # Pre-populate from JobSeekerProfile if available
    initial = {}
    try:
        profile = request.user.jobseeker_profile
        initial['full_name']           = request.user.get_full_name() or ''
        initial['applicant_location']  = profile.location or ''
        skills_qs = profile.skills.all()
        if skills_qs.exists():
            initial['skills_summary'] = ', '.join(s.name for s in skills_qs)
        exp_qs = profile.experience.order_by('-start_date')
        if exp_qs.exists():
            lines = []
            for e in exp_qs[:3]:
                dur = f"{e.start_date.strftime('%b %Y')} – {'Present' if e.is_current else e.end_date.strftime('%b %Y') if e.end_date else 'Present'}"
                lines.append(f"{e.job_title} at {e.company} ({dur})")
            initial['experience_summary'] = '\n'.join(lines)
    except Exception:
        pass

    if request.method == 'POST':
        form = ApplyForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.job = job
            app.applicant = request.user

            # Attach selected existing resume
            resume_id = request.POST.get('resume_id')
            if resume_id:
                try:
                    app.resume = Resume.objects.get(pk=resume_id, user=request.user)
                except Resume.DoesNotExist:
                    pass

            app.save()
            messages.success(request, f'Application submitted for "{job.title}"!')

            # Auto-compute AI match score in the background (silent — don't block apply)
            try:
                from screening.engine import compute_match
                from screening.models import MatchScore
                result = compute_match(job, request.user)
                MatchScore.objects.update_or_create(
                    job=job,
                    candidate=request.user,
                    defaults={
                        'skills_score':           result['skills_score'],
                        'experience_score':       result['experience_score'],
                        'education_score':        result['education_score'],
                        'keywords_score':         result['keywords_score'],
                        'total_score':            result['total_score'],
                        'matched_skills':         result['matched_skills'],
                        'missing_skills':         result['missing_skills'],
                        'matched_keywords':       result['matched_keywords'],
                        'experience_years_found': result['experience_years_found'],
                        'education_rank_found':   result['education_rank_found'],
                    },
                )
            except Exception:
                pass  # Never block the application submit

            # Notify the recruiter
            recruiter_user = job.recruiter.user
            applicant_name = request.user.get_full_name() or request.user.email
            notify(recruiter_user, Notification.TYPE_APP_RECEIVED,
                   title=f'New application: {job.title}',
                   message=f'{applicant_name} applied for {job.title}.',
                   link=f'/applications/jobs/{job.pk}/applicants/',
                   from_user=request.user)
            return redirect('jobs:detail', pk=pk)
    else:
        form = ApplyForm(initial=initial)

    return render(request, 'applications/apply.html', {
        'job':          job,
        'form':         form,
        'skills':       job.get_skills_list(),
        'user_resumes': user_resumes,
    })


# ---------------------------------------------------------------------------
# Job Seeker: Withdraw
# ---------------------------------------------------------------------------

@login_required
@require_POST
def withdraw(request, pk):
    """Job seeker withdraws their application (only if still pending)."""
    app = get_object_or_404(Application, pk=pk, applicant=request.user)
    if app.status == Application.STATUS_PENDING:
        job_title = app.job.title
        app.delete()
        messages.success(request, f'Application for "{job_title}" withdrawn.')
    else:
        messages.error(request, "You can only withdraw pending applications.")
    return redirect('applications:my_applications')


# ---------------------------------------------------------------------------
# Job Seeker: My Applications
# ---------------------------------------------------------------------------

@login_required
def my_applications(request):
    """Job seeker view: all their applications, newest first."""
    if not _is_job_seeker(request.user):
        return redirect('jobs:board')

    apps = (Application.objects
            .filter(applicant=request.user)
            .select_related('job', 'job__recruiter')
            .order_by('-applied_at'))

    counts = {
        'total':       apps.count(),
        'pending':     apps.filter(status='pending').count(),
        'shortlisted': apps.filter(status='shortlisted').count(),
        'hired':       apps.filter(status='hired').count(),
    }
    from feedback.models import Feedback
    rated_company_ids = set(
        Feedback.objects.filter(from_user=request.user, feedback_type=Feedback.TYPE_C2CO)
        .values_list('application_id', flat=True)
    )
    return render(request, 'applications/my_applications.html', {
        'applications':      apps,
        'counts':            counts,
        'rated_company_ids': rated_company_ids,
    })


# ---------------------------------------------------------------------------
# Recruiter: All Applications (across all jobs)
# ---------------------------------------------------------------------------

@login_required
def all_applications(request):
    """Recruiter view: all applications across all their jobs."""
    if not _is_recruiter(request.user):
        messages.error(request, "Only recruiters can view applications.")
        return redirect('jobs:board')

    try:
        profile = request.user.recruiter_profile
    except Exception:
        return redirect('jobs:board')

    # Filter
    status_filter = request.GET.get('status', '')
    job_filter    = request.GET.get('job', '')

    apps = (Application.objects
            .filter(job__recruiter=profile)
            .select_related('job', 'applicant', 'resume')
            .order_by('-applied_at'))

    if status_filter:
        apps = apps.filter(status=status_filter)
    if job_filter:
        apps = apps.filter(job_id=job_filter)

    from screening.models import MatchScore
    score_map = {
        ms.candidate_id: ms
        for ms in MatchScore.objects.filter(job__recruiter=profile)
    }
    for app in apps:
        app.match_score = score_map.get(app.applicant_id)

    jobs_list = profile.jobs.order_by('-created_at')
    counts = {
        'total':       apps.count(),
        'pending':     apps.filter(status='pending').count(),
        'shortlisted': apps.filter(status='shortlisted').count(),
        'hired':       apps.filter(status='hired').count(),
        'rejected':    apps.filter(status='rejected').count(),
    }

    return render(request, 'applications/all_applications.html', {
        'applications':           apps,
        'jobs_list':              jobs_list,
        'counts':                 counts,
        'status_filter':          status_filter,
        'job_filter':             job_filter,
        'total_application_count': counts['total'],
        'profile':                profile,
    })


# ---------------------------------------------------------------------------
# Recruiter: Applicants for a Job
# ---------------------------------------------------------------------------

@login_required
def job_applicants(request, pk):
    """Recruiter view: all applicants for one job."""
    if not _is_recruiter(request.user):
        messages.error(request, "Only recruiters can view applicants.")
        return redirect('jobs:board')

    job = get_object_or_404(JobPost, pk=pk)
    try:
        if job.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('jobs:manage')
    except Exception:
        return redirect('jobs:manage')

    apps = (Application.objects
            .filter(job=job)
            .select_related('applicant')
            .order_by('-applied_at'))

    # Pre-fetch match scores for this job to link in template
    from screening.models import MatchScore
    score_map = {
        ms.candidate_id: ms
        for ms in MatchScore.objects.filter(job=job)
    }
    # Attach score to each application for template use
    for app in apps:
        app.match_score = score_map.get(app.applicant_id)

    from feedback.models import Feedback
    rated_candidate_ids = set(
        Feedback.objects.filter(feedback_type=Feedback.TYPE_CO2C, application__job=job)
        .values_list('application_id', flat=True)
    )

    counts = {
        'total':       apps.count(),
        'pending':     apps.filter(status='pending').count(),
        'shortlisted': apps.filter(status='shortlisted').count(),
        'hired':       apps.filter(status='hired').count(),
        'rejected':    apps.filter(status='rejected').count(),
    }
    return render(request, 'applications/applicants.html', {
        'job':                job,
        'applications':       apps,
        'counts':             counts,
        'rated_candidate_ids': rated_candidate_ids,
    })


# ---------------------------------------------------------------------------
# Recruiter: Update Application Status
# ---------------------------------------------------------------------------

@login_required
@require_POST
def update_application_status(request, pk):
    """Recruiter updates the status and optional notes for an application."""
    app = get_object_or_404(Application, pk=pk)

    if not _is_recruiter(request.user):
        return redirect('applications:applicants', pk=app.job_id)

    try:
        if app.job.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('jobs:manage')
    except Exception:
        return redirect('jobs:manage')

    new_status = request.POST.get('status', '')
    valid = [c[0] for c in Application.STATUS_CHOICES]
    if new_status in valid:
        old_status = app.status
        app.status = new_status
        app.recruiter_notes = request.POST.get('notes', '').strip()
        app.save(update_fields=['status', 'recruiter_notes', 'updated_at'])

        # Notify applicant on meaningful status changes
        if new_status != old_status:
            company = app.job.recruiter.company_name
            job_title = app.job.title
            recruiter_user = app.job.recruiter.user
            if new_status == 'shortlisted':
                notify(app.applicant, Notification.TYPE_SHORTLISTED,
                       title=f'You\'ve been shortlisted for {job_title}',
                       message=f'{company} has shortlisted your application.',
                       link='/applications/my-applications/',
                       from_user=recruiter_user)
            elif new_status == 'rejected':
                notify(app.applicant, Notification.TYPE_REJECTED,
                       title=f'Application update: {job_title}',
                       message=f'{company} has reviewed and declined your application.',
                       link='/applications/my-applications/',
                       from_user=recruiter_user)
            elif new_status == 'hired':
                notify(app.applicant, Notification.TYPE_HIRED,
                       title=f'Congratulations! Offer from {company}',
                       message=f'You have been selected for {job_title} at {company}!',
                       link='/applications/my-applications/',
                       from_user=recruiter_user)

    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and next_url.startswith('/'):
        return redirect(next_url)
    return redirect('applications:applicants', pk=app.job_id)


# ---------------------------------------------------------------------------
# Resume Download (recruiter only — forces browser download)
# ---------------------------------------------------------------------------

@login_required
def download_resume(request, pk, resume_type):
    """Serve an applicant's resume as a forced download for the recruiter."""
    app = get_object_or_404(Application, pk=pk)

    if not _is_recruiter(request.user):
        raise Http404

    try:
        if app.job.recruiter != request.user.recruiter_profile:
            raise Http404
    except Exception:
        raise Http404

    if resume_type == 'profile':
        if not app.resume or not app.resume.file:
            raise Http404
        file_field = app.resume.file
        filename   = app.resume.original_filename or os.path.basename(app.resume.file.name)
    elif resume_type == 'uploaded':
        if not app.resume_file:
            raise Http404
        file_field = app.resume_file
        filename   = os.path.basename(app.resume_file.name)
    else:
        raise Http404

    content_type, _ = mimetypes.guess_type(filename)
    content_type = content_type or 'application/octet-stream'

    response = FileResponse(file_field.open('rb'), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
