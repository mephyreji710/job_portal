from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import JobSeekerProfile, Skill, Education, Experience, Certification
from .forms import (
    PersonalDetailsForm, SkillForm,
    EducationForm, ExperienceForm, CertificationForm,
)


def _require_jobseeker(request):
    """Return (or create) the profile if user is a job seeker, else None."""
    if not request.user.is_job_seeker_user():
        messages.error(request, 'This section is for job seekers only.')
        return None
    profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
    return profile


# ---------------------------------------------------------------------------
# Profile Overview
# ---------------------------------------------------------------------------

@login_required
def profile_view(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    return render(request, 'jobseeker/profile.html', {'profile': profile})


# ---------------------------------------------------------------------------
# Personal Details
# ---------------------------------------------------------------------------

@login_required
def personal_edit(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')

    form = PersonalDetailsForm(
        request.POST or None,
        request.FILES or None,
        instance=profile,
        user=request.user,
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Personal details updated!')
            return redirect('jobseeker:profile')
        messages.error(request, 'Please fix the errors below.')

    return render(request, 'jobseeker/personal_edit.html', {
        'form': form, 'profile': profile,
    })


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

@login_required
def skills_manage(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')

    form = SkillForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        skill = form.save(commit=False)
        skill.profile = profile
        try:
            skill.save()
            messages.success(request, f'Skill "{skill.name}" added!')
        except Exception:
            messages.error(request, f'"{skill.name}" is already in your list.')
        return redirect('jobseeker:skills')

    return render(request, 'jobseeker/skills.html', {
        'profile': profile, 'form': form, 'skills': profile.skills.all(),
    })


@login_required
def skill_delete(request, pk):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    skill = get_object_or_404(Skill, pk=pk, profile=profile)
    if request.method == 'POST':
        messages.success(request, f'Skill "{skill.name}" removed.')
        skill.delete()
    return redirect('jobseeker:skills')


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------

@login_required
def education_manage(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    return render(request, 'jobseeker/education.html', {
        'profile': profile, 'entries': profile.education.all(),
    })


@login_required
def education_add(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    form = EducationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        edu = form.save(commit=False)
        edu.profile = profile
        edu.save()
        messages.success(request, 'Education entry added!')
        return redirect('jobseeker:education')
    return render(request, 'jobseeker/education_form.html', {
        'form': form, 'profile': profile, 'action': 'Add',
    })


@login_required
def education_edit(request, pk):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    edu = get_object_or_404(Education, pk=pk, profile=profile)
    form = EducationForm(request.POST or None, instance=edu)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Education entry updated!')
        return redirect('jobseeker:education')
    return render(request, 'jobseeker/education_form.html', {
        'form': form, 'profile': profile, 'action': 'Edit', 'object': edu,
    })


@login_required
def education_delete(request, pk):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    edu = get_object_or_404(Education, pk=pk, profile=profile)
    if request.method == 'POST':
        edu.delete()
        messages.success(request, 'Education entry removed.')
    return redirect('jobseeker:education')


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

@login_required
def experience_manage(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    return render(request, 'jobseeker/experience.html', {
        'profile': profile, 'entries': profile.experience.all(),
    })


@login_required
def experience_add(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    form = ExperienceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        exp = form.save(commit=False)
        exp.profile = profile
        exp.save()
        messages.success(request, 'Experience added!')
        return redirect('jobseeker:experience')
    return render(request, 'jobseeker/experience_form.html', {
        'form': form, 'profile': profile, 'action': 'Add',
    })


@login_required
def experience_edit(request, pk):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    exp = get_object_or_404(Experience, pk=pk, profile=profile)
    form = ExperienceForm(request.POST or None, instance=exp)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Experience updated!')
        return redirect('jobseeker:experience')
    return render(request, 'jobseeker/experience_form.html', {
        'form': form, 'profile': profile, 'action': 'Edit', 'object': exp,
    })


@login_required
def experience_delete(request, pk):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    exp = get_object_or_404(Experience, pk=pk, profile=profile)
    if request.method == 'POST':
        exp.delete()
        messages.success(request, 'Experience removed.')
    return redirect('jobseeker:experience')


# ---------------------------------------------------------------------------
# Certifications
# ---------------------------------------------------------------------------

@login_required
def certifications_manage(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    return render(request, 'jobseeker/certifications.html', {
        'profile': profile, 'entries': profile.certifications.all(),
    })


@login_required
def certification_add(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    form = CertificationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cert = form.save(commit=False)
        cert.profile = profile
        cert.save()
        messages.success(request, 'Certification added!')
        return redirect('jobseeker:certifications')
    return render(request, 'jobseeker/certification_form.html', {
        'form': form, 'profile': profile, 'action': 'Add',
    })


@login_required
def certification_edit(request, pk):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    cert = get_object_or_404(Certification, pk=pk, profile=profile)
    form = CertificationForm(request.POST or None, instance=cert)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Certification updated!')
        return redirect('jobseeker:certifications')
    return render(request, 'jobseeker/certification_form.html', {
        'form': form, 'profile': profile, 'action': 'Edit', 'object': cert,
    })


@login_required
def certification_delete(request, pk):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')
    cert = get_object_or_404(Certification, pk=pk, profile=profile)
    if request.method == 'POST':
        cert.delete()
        messages.success(request, 'Certification removed.')
    return redirect('jobseeker:certifications')
