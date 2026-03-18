import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from jobseeker.models import JobSeekerProfile, Skill
from .models import Resume
from .forms import ResumeUploadForm
from .parser import run_parse_and_save


def _get_profile(request):
    """Return (or create) the JobSeekerProfile for sidebar rendering."""
    profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
    return profile


def _require_jobseeker(request):
    """Ensure user is a job seeker; return profile or None."""
    if not request.user.is_authenticated or not request.user.is_job_seeker_user():
        messages.error(request, 'This section is for job seekers only.')
        return None
    return _get_profile(request)


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

@login_required
def upload(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['file']
            ext = os.path.splitext(f.name)[1].lower().lstrip('.')
            resume = Resume.objects.create(
                user=request.user,
                file=f,
                original_filename=f.name,
                file_type=ext,
                file_size=f.size,
            )
            try:
                run_parse_and_save(resume)
                parsed = getattr(resume, 'parsed', None)
                skill_count = parsed.tech_skill_count if parsed else 0
                messages.success(
                    request,
                    f'Resume uploaded and parsed! Found {skill_count} technical skill(s).'
                )
            except Exception as exc:
                resume.status = 'failed'
                resume.parse_error = str(exc)[:500]
                resume.save(update_fields=['status', 'parse_error'])
                messages.warning(
                    request,
                    f'Resume uploaded but parsing failed: {str(exc)[:120]}. '
                    f'You can retry parsing from the resume detail page.'
                )
            return redirect('resume:detail', pk=resume.pk)
    else:
        form = ResumeUploadForm()

    return render(request, 'resume/upload.html', {
        'form': form,
        'profile': profile,
    })


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

@login_required
def resume_list(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')

    resumes = Resume.objects.filter(user=request.user).select_related('parsed')
    return render(request, 'resume/list.html', {
        'resumes': resumes,
        'profile': profile,
    })


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------

@login_required
def detail(request, pk):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')

    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    parsed = getattr(resume, 'parsed', None)
    keywords_tech = []
    keywords_soft = []
    keywords_other = []
    if parsed:
        qs = parsed.keywords.all()
        keywords_tech  = [k for k in qs if k.category == 'tech']
        keywords_soft  = [k for k in qs if k.category == 'soft']
        keywords_other = [k for k in qs if k.category == 'other']

    return render(request, 'resume/detail.html', {
        'resume': resume,
        'parsed': parsed,
        'profile': profile,
        'keywords_tech': keywords_tech,
        'keywords_soft': keywords_soft,
        'keywords_other': keywords_other,
    })


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@login_required
def delete(request, pk):
    if request.method == 'POST':
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
        fname = resume.original_filename
        try:
            resume.file.delete(save=False)
        except Exception:
            pass
        resume.delete()
        messages.success(request, f'"{fname}" has been deleted.')
    return redirect('resume:list')


# ---------------------------------------------------------------------------
# Re-parse
# ---------------------------------------------------------------------------

@login_required
def reparse(request, pk):
    if request.method == 'POST':
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
        try:
            run_parse_and_save(resume)
            messages.success(request, 'Resume re-parsed successfully.')
        except Exception as exc:
            messages.error(request, f'Re-parsing failed: {str(exc)[:120]}')
    return redirect('resume:detail', pk=pk)


# ---------------------------------------------------------------------------
# Set Primary
# ---------------------------------------------------------------------------

@login_required
def set_primary(request, pk):
    if request.method == 'POST':
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
        Resume.objects.filter(user=request.user).update(is_primary=False)
        resume.is_primary = True
        resume.save(update_fields=['is_primary'])
        messages.success(request, f'"{resume.original_filename}" is now your primary resume.')
    return redirect('resume:list')


# ---------------------------------------------------------------------------
# Apply skills to profile
# ---------------------------------------------------------------------------

@login_required
def apply_to_profile(request, pk):
    """Sync tech skills extracted from a parsed resume into the JobSeekerProfile."""
    if request.method != 'POST':
        return redirect('resume:detail', pk=pk)

    profile = _require_jobseeker(request)
    if profile is None:
        return redirect('accounts:dashboard')

    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    parsed = getattr(resume, 'parsed', None)

    if not parsed:
        messages.error(request, 'This resume has not been parsed yet. Please re-parse first.')
        return redirect('resume:detail', pk=pk)

    added = 0
    for skill_data in parsed.extracted_skills:
        name = skill_data.get('name', '').strip()
        if not name:
            continue
        if not profile.skills.filter(name__iexact=name).exists():
            Skill.objects.create(
                profile=profile,
                name=name,
                proficiency='intermediate',
            )
            added += 1

    if added:
        messages.success(request, f'Added {added} new skill(s) to your profile from this resume.')
    else:
        messages.info(request, 'No new skills to add — all detected skills are already in your profile.')

    return redirect('resume:detail', pk=pk)
