from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.models import RecruiterProfile
from .forms import CompanyProfileForm, HRMemberForm
from .models import HRMember


def _require_recruiter(request):
    """Ensure user is authenticated and is a recruiter. Returns profile or None."""
    if not request.user.is_authenticated or not request.user.is_recruiter_user():
        messages.error(request, 'This section is for recruiters only.')
        return None
    profile, _ = RecruiterProfile.objects.get_or_create(
        user=request.user,
        defaults={'company_name': 'My Company'},
    )
    return profile


# ---------------------------------------------------------------------------
# Company Panel (overview)
# ---------------------------------------------------------------------------

@login_required
def company_panel(request):
    profile = _require_recruiter(request)
    if profile is None:
        return redirect('accounts:dashboard')

    from jobs.models import JobPost
    from applications.models import Application
    from feedback.models import Feedback
    from django.db.models import Avg

    job_ids = list(profile.jobs.values_list('id', flat=True))
    apps = Application.objects.filter(job_id__in=job_ids)

    avg = Feedback.objects.filter(
        application__job_id__in=job_ids, feedback_type=Feedback.TYPE_C2CO
    ).aggregate(avg=Avg('rating'))['avg']

    # Assessment counts
    try:
        from assessments.models import Assessment, AssessmentAttempt
        assessments_sent = Assessment.objects.filter(application__job_id__in=job_ids).count()
        assessments_completed = AssessmentAttempt.objects.filter(
            assessment__application__job_id__in=job_ids, is_completed=True
        ).count()
    except Exception:
        assessments_sent = 0
        assessments_completed = 0

    stats = {
        'active_jobs':           profile.jobs.filter(status=JobPost.STATUS_ACTIVE).count(),
        'total_applied':         apps.count(),
        'pending':               apps.filter(status='pending').count(),
        'reviewed':              apps.filter(status='reviewed').count(),
        'shortlisted':           apps.filter(status='shortlisted').count(),
        'rejected':              apps.filter(status='rejected').count(),
        'hired':                 apps.filter(status='hired').count(),
        'assessments_sent':      assessments_sent,
        'assessments_completed': assessments_completed,
        'avg_rating':            round(avg, 1) if avg else None,
    }

    recent_apps = apps.select_related('job', 'applicant').order_by('-applied_at')[:6]

    return render(request, 'recruiter/panel.html', {
        'profile':     profile,
        'stats':       stats,
        'recent_apps': recent_apps,
    })


# ---------------------------------------------------------------------------
# Edit Company Profile
# ---------------------------------------------------------------------------

@login_required
def edit_profile(request):
    profile = _require_recruiter(request)
    if profile is None:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company profile updated successfully.')
            return redirect('recruiter:panel')
    else:
        form = CompanyProfileForm(instance=profile)

    return render(request, 'recruiter/edit.html', {'profile': profile, 'form': form})


# ---------------------------------------------------------------------------
# HR Team
# ---------------------------------------------------------------------------

@login_required
def hr_team(request):
    profile = _require_recruiter(request)
    if profile is None:
        return redirect('accounts:dashboard')

    form = HRMemberForm()
    members = profile.hr_members.all()
    return render(request, 'recruiter/team.html', {
        'profile': profile,
        'members': members,
        'form': form,
    })


@login_required
def add_hr_member(request):
    profile = _require_recruiter(request)
    if profile is None:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = HRMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.company = profile
            try:
                member.save()
                messages.success(request, f'{member.name} added to HR team.')
            except Exception:
                messages.error(request, 'That email address is already in your team.')
        else:
            for field, errors in form.errors.items():
                for e in errors:
                    messages.error(request, f'{field.capitalize()}: {e}')
    return redirect('recruiter:team')


@login_required
def remove_hr_member(request, pk):
    profile = _require_recruiter(request)
    if profile is None:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        member = get_object_or_404(HRMember, pk=pk, company=profile)
        name = member.name
        member.delete()
        messages.success(request, f'{name} removed from HR team.')
    return redirect('recruiter:team')


# ---------------------------------------------------------------------------
# Active Jobs (placeholder — filled by Module 5: Job Listings)
# ---------------------------------------------------------------------------

@login_required
def jobs_list(request):
    """Redirect to the dedicated job management page (Module 5)."""
    profile = _require_recruiter(request)
    if profile is None:
        return redirect('accounts:dashboard')
    return redirect('jobs:manage')


# ---------------------------------------------------------------------------
# Public Company Profile (visible to anyone)
# ---------------------------------------------------------------------------

def public_company_profile(request, pk):
    from jobs.models import JobPost
    profile = get_object_or_404(RecruiterProfile, pk=pk)
    active_jobs = profile.jobs.filter(status=JobPost.STATUS_ACTIVE).order_by('-created_at')
    return render(request, 'recruiter/public_profile.html', {
        'profile': profile,
        'active_jobs': active_jobs,
    })
