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
        defaults={'company_name': request.user.get_full_name() or request.user.username},
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
    avg = Feedback.objects.filter(
        application__job_id__in=job_ids, feedback_type=Feedback.TYPE_C2CO
    ).aggregate(avg=Avg('rating'))['avg']
    stats = {
        'active_jobs':   profile.jobs.filter(status=JobPost.STATUS_ACTIVE).count(),
        'total_applied': Application.objects.filter(job_id__in=job_ids).count(),
        'shortlisted':   Application.objects.filter(job_id__in=job_ids, status='shortlisted').count(),
        'avg_rating':    round(avg, 1) if avg else None,
    }
    return render(request, 'recruiter/panel.html', {'profile': profile, 'stats': stats})


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
