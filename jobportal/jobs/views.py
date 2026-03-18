from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from django.views.decorators.http import require_POST

from accounts.models import RecruiterProfile
from .models import JobPost, SavedJob
from .forms import JobPostForm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_recruiter_profile(request):
    if not request.user.is_authenticated or not request.user.is_recruiter_user():
        return None
    profile, _ = RecruiterProfile.objects.get_or_create(
        user=request.user,
        defaults={'company_name': request.user.get_full_name() or request.user.username},
    )
    return profile


def _own_job(request, pk):
    """Return the job if it belongs to the current recruiter, else None."""
    profile = _get_recruiter_profile(request)
    if profile is None:
        return None, profile
    job = get_object_or_404(JobPost, pk=pk, recruiter=profile)
    return job, profile


# ---------------------------------------------------------------------------
# Public: Job Board
# ---------------------------------------------------------------------------

def job_board(request):
    qs = JobPost.objects.filter(status=JobPost.STATUS_ACTIVE).select_related('recruiter')

    q         = request.GET.get('q', '').strip()
    job_type  = request.GET.get('type', '')
    location  = request.GET.get('location', '').strip()
    exp_level = request.GET.get('exp', '')

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(recruiter__company_name__icontains=q) |
            Q(required_skills__icontains=q) |
            Q(description__icontains=q)
        )
    if job_type:
        qs = qs.filter(job_type=job_type)
    if location:
        qs = qs.filter(Q(location__icontains=location) | Q(is_remote=True))
    if exp_level:
        qs = qs.filter(experience_level=exp_level)

    # Pass saved job IDs for the current job seeker so cards show the right bookmark state
    saved_ids = set()
    if request.user.is_authenticated and getattr(request.user, 'role', None) == 'job_seeker':
        saved_ids = set(SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True))

    return render(request, 'jobs/job_board.html', {
        'jobs':           qs,
        'total':          qs.count(),
        'q':              q,
        'filter_type':    job_type,
        'filter_location':location,
        'filter_exp':     exp_level,
        'job_type_choices':   JobPost.JOB_TYPE_CHOICES,
        'experience_choices': JobPost.EXPERIENCE_CHOICES,
        'saved_ids':          saved_ids,
    })


# ---------------------------------------------------------------------------
# Public: Job Detail
# ---------------------------------------------------------------------------

def job_detail(request, pk):
    job = get_object_or_404(JobPost, pk=pk, status=JobPost.STATUS_ACTIVE)
    # Increment view count
    JobPost.objects.filter(pk=pk).update(views_count=job.views_count + 1)

    is_owner = (
        request.user.is_authenticated and
        request.user.is_recruiter_user() and
        hasattr(request.user, 'recruiter_profile') and
        job.recruiter_id == request.user.recruiter_profile.id
    )

    existing_score = None
    existing_application = None
    is_saved = False
    if request.user.is_authenticated and not is_owner:
        try:
            from screening.models import MatchScore
            existing_score = MatchScore.objects.filter(job=job, candidate=request.user).first()
        except Exception:
            pass
        try:
            from applications.models import Application
            existing_application = Application.objects.filter(job=job, applicant=request.user).first()
        except Exception:
            pass
        if getattr(request.user, 'role', None) == 'job_seeker':
            is_saved = SavedJob.objects.filter(user=request.user, job=job).exists()

    return render(request, 'jobs/job_detail.html', {
        'job':                  job,
        'is_owner':             is_owner,
        'skills':               job.get_skills_list(),
        'existing_score':       existing_score,
        'existing_application': existing_application,
        'is_saved':             is_saved,
    })


# ---------------------------------------------------------------------------
# Recruiter: My Jobs (management list)
# ---------------------------------------------------------------------------

@login_required
def manage(request):
    profile = _get_recruiter_profile(request)
    if profile is None:
        messages.error(request, 'This section is for recruiters only.')
        return redirect('accounts:dashboard')

    status_filter = request.GET.get('status', '')
    qs = JobPost.objects.filter(recruiter=profile)
    if status_filter:
        qs = qs.filter(status=status_filter)

    counts = {
        'all':    JobPost.objects.filter(recruiter=profile).count(),
        'active': JobPost.objects.filter(recruiter=profile, status='active').count(),
        'draft':  JobPost.objects.filter(recruiter=profile, status='draft').count(),
        'paused': JobPost.objects.filter(recruiter=profile, status='paused').count(),
        'closed': JobPost.objects.filter(recruiter=profile, status='closed').count(),
    }
    return render(request, 'jobs/manage.html', {
        'profile':       profile,
        'jobs':          qs,
        'counts':        counts,
        'status_filter': status_filter,
    })


# ---------------------------------------------------------------------------
# Recruiter: Create Job
# ---------------------------------------------------------------------------

@login_required
def job_new(request):
    profile = _get_recruiter_profile(request)
    if profile is None:
        messages.error(request, 'This section is for recruiters only.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = profile
            job.save()
            messages.success(request, f'Job "{job.title}" created successfully.')
            return redirect('jobs:manage')
    else:
        form = JobPostForm(initial={
            'location': profile.location,
            'salary_currency': 'USD',
        })

    return render(request, 'jobs/job_form.html', {
        'form':    form,
        'profile': profile,
        'is_edit': False,
    })


# ---------------------------------------------------------------------------
# Recruiter: Edit Job
# ---------------------------------------------------------------------------

@login_required
def job_edit(request, pk):
    job, profile = _own_job(request, pk)
    if profile is None:
        messages.error(request, 'This section is for recruiters only.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{job.title}" updated.')
            return redirect('jobs:manage')
    else:
        form = JobPostForm(instance=job)

    return render(request, 'jobs/job_form.html', {
        'form':    form,
        'profile': profile,
        'job':     job,
        'is_edit': True,
    })


# ---------------------------------------------------------------------------
# Recruiter: Delete Job
# ---------------------------------------------------------------------------

@login_required
def job_delete(request, pk):
    if request.method == 'POST':
        job, profile = _own_job(request, pk)
        if profile is None:
            return redirect('accounts:dashboard')
        title = job.title
        job.delete()
        messages.success(request, f'"{title}" has been deleted.')
    return redirect('jobs:manage')


# ---------------------------------------------------------------------------
# Recruiter: Toggle Status (draft ↔ active, active → paused, any → closed)
# ---------------------------------------------------------------------------

@login_required
def job_toggle_status(request, pk):
    if request.method == 'POST':
        job, profile = _own_job(request, pk)
        if profile is None:
            return redirect('accounts:dashboard')

        action = request.POST.get('action', '')
        transitions = {
            'activate': JobPost.STATUS_ACTIVE,
            'pause':    JobPost.STATUS_PAUSED,
            'draft':    JobPost.STATUS_DRAFT,
            'close':    JobPost.STATUS_CLOSED,
        }
        new_status = transitions.get(action)
        if new_status:
            job.status = new_status
            job.save(update_fields=['status'])
            messages.success(request, f'"{job.title}" status changed to {job.get_status_display()}.')
    return redirect('jobs:manage')


# ---------------------------------------------------------------------------
# Recruiter: Detail (own job preview with stats)
# ---------------------------------------------------------------------------

@login_required
def job_detail_recruiter(request, pk):
    job, profile = _own_job(request, pk)
    if profile is None:
        messages.error(request, 'This section is for recruiters only.')
        return redirect('accounts:dashboard')
    return render(request, 'jobs/job_detail_recruiter.html', {
        'job':     job,
        'profile': profile,
        'skills':  job.get_skills_list(),
    })


# ---------------------------------------------------------------------------
# Job Seeker: Save / Unsave (Wishlist)
# ---------------------------------------------------------------------------

@login_required
@require_POST
def toggle_save(request, pk):
    """Toggle save state for a job. Only job seekers may save jobs."""
    if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'job_seeker':
        messages.error(request, "Only job seekers can save jobs.")
        return redirect('jobs:detail', pk=pk)

    job = get_object_or_404(JobPost, pk=pk)
    saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created:
        saved.delete()

    # Return to wherever the user came from
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'jobs:board'
    if next_url.startswith('http'):
        return redirect(next_url)
    return redirect(next_url)


@login_required
def saved_jobs(request):
    """Job seeker view: their bookmarked / saved jobs."""
    if getattr(request.user, 'role', None) != 'job_seeker':
        return redirect('jobs:board')

    saves = (SavedJob.objects
             .filter(user=request.user)
             .select_related('job', 'job__recruiter')
             .order_by('-saved_at'))

    return render(request, 'jobs/saved_jobs.html', {
        'saves': saves,
        'count': saves.count(),
    })
