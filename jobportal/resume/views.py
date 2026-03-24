import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from jobseeker.models import JobSeekerProfile, Skill
from .models import Resume, BuiltResume
from .forms import ResumeUploadForm, BuiltResumeForm
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


# ---------------------------------------------------------------------------
# Resume Builder
# ---------------------------------------------------------------------------

@login_required
def builder_list(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect("accounts:login")
    built_resumes = BuiltResume.objects.filter(user=request.user)
    return render(request, "resume/builder_list.html", {
        "profile":       profile,
        "built_resumes": built_resumes,
    })


@login_required
def builder_create(request):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect("accounts:login")
    if request.method == "POST":
        form = BuiltResumeForm(request.POST)
        if form.is_valid():
            br = form.save(commit=False)
            br.user = request.user
            br.save()
            messages.success(request, f'Resume "{br.title}" created!')
            return redirect("resume:builder_preview", pk=br.pk)
    else:
        # Pre-fill contact from profile
        initial = {
            "custom_name":     request.user.get_full_name(),
            "custom_email":    request.user.email,
            "custom_phone":    getattr(request.user, "phone", "") or "",
            "custom_location": profile.location,
            "custom_linkedin": profile.linkedin_url,
            "custom_website":  profile.website,
            "summary":         profile.bio,
        }
        form = BuiltResumeForm(initial=initial)
    return render(request, "resume/builder_form.html", {
        "profile": profile,
        "form":    form,
        "action":  "Create",
    })


@login_required
def builder_edit(request, pk):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect("accounts:login")
    br = get_object_or_404(BuiltResume, pk=pk, user=request.user)
    if request.method == "POST":
        form = BuiltResumeForm(request.POST, instance=br)
        if form.is_valid():
            form.save()
            messages.success(request, "Resume updated.")
            return redirect("resume:builder_preview", pk=br.pk)
    else:
        form = BuiltResumeForm(instance=br)
    return render(request, "resume/builder_form.html", {
        "profile": profile,
        "form":    form,
        "action":  "Save Changes",
        "resume":  br,
    })


@login_required
def builder_preview(request, pk):
    profile = _require_jobseeker(request)
    if profile is None:
        return redirect("accounts:login")
    br = get_object_or_404(BuiltResume, pk=pk, user=request.user)

    # ── Contact (override > profile) ──────────────────────────────────────
    ctx_name     = br.custom_name     or request.user.get_full_name() or request.user.email
    ctx_email    = br.custom_email    or request.user.email
    ctx_phone    = br.custom_phone    or getattr(request.user, "phone", "") or ""
    ctx_location = br.custom_location or profile.location
    ctx_linkedin = br.custom_linkedin or profile.linkedin_url
    ctx_website  = br.custom_website  or profile.website

    # ── Font resolution ────────────────────────────────────────────────────
    FONT_STACKS = {
        'sans':       ("-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif", None),
        'inter':      ("'Inter', 'Segoe UI', Arial, sans-serif",
                       "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap"),
        'serif':      ("Georgia, Cambria, 'Times New Roman', serif", None),
        'montserrat': ("'Montserrat', Arial, sans-serif",
                       "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap"),
        'raleway':    ("'Raleway', 'Segoe UI', sans-serif",
                       "https://fonts.googleapis.com/css2?family=Raleway:wght@400;600;700;800&display=swap"),
    }
    font_stack, font_url = FONT_STACKS.get(br.font_family or 'sans', FONT_STACKS['sans'])

    # ── Accent colour (template default if blank) ──────────────────────────
    DEFAULT_ACCENTS = {
        'classic': '#1d4ed8',
        'modern':  '#0891b2',
        'sidebar': '#6366f1',
    }
    accent = br.accent_color or DEFAULT_ACCENTS.get(br.template_name, '#4f46e5')

    # ── Section order ──────────────────────────────────────────────────────
    ALL_SECTIONS = ['summary', 'experience', 'skills', 'education', 'certs']
    raw_order = br.section_order or ','.join(ALL_SECTIONS)
    sections  = [s.strip() for s in raw_order.split(',') if s.strip() in ALL_SECTIONS]
    # Append any missing sections at the end (safety net)
    for s in ALL_SECTIONS:
        if s not in sections:
            sections.append(s)

    template_map = {
        "classic": "resume/preview_classic.html",
        "modern":  "resume/preview_modern.html",
        "sidebar": "resume/preview_sidebar.html",
    }
    tpl = template_map.get(br.template_name, "resume/preview_classic.html")
    return render(request, tpl, {
        "br":         br,
        "profile":    profile,
        "name":       ctx_name,
        "email":      ctx_email,
        "phone":      ctx_phone,
        "location":   ctx_location,
        "linkedin":   ctx_linkedin,
        "website":    ctx_website,
        "headline":   profile.headline,
        "summary":    br.summary or profile.bio,
        "skills":     profile.skills.all(),
        "experience": profile.experience.all(),
        "education":  profile.education.all(),
        "certs":      profile.certifications.all(),
        # customisation
        "accent":     accent,
        "font_stack": font_stack,
        "font_url":   font_url,
        "sections":   sections,
    })


@login_required
def builder_delete(request, pk):
    br = get_object_or_404(BuiltResume, pk=pk, user=request.user)
    if request.method == "POST":
        title = br.title
        br.delete()
        messages.success(request, f"Resume \"{title}\" deleted.")
    return redirect("resume:builder_list")
