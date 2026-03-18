from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from jobs.models import JobPost
from .models import MatchScore
from .engine import compute_match


def _is_job_seeker(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'job_seeker'


def _is_recruiter(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'recruiter'


@login_required
@require_POST
def check_match(request, pk):
    """Compute (or recompute) the match score for the current job seeker."""
    if not _is_job_seeker(request.user):
        messages.error(request, "Only job seekers can check match scores.")
        return redirect('jobs:detail', pk=pk)

    job = get_object_or_404(JobPost, pk=pk, status='active')
    result = compute_match(job, request.user)

    score, _ = MatchScore.objects.update_or_create(
        job=job,
        candidate=request.user,
        defaults={
            'skills_score':          result['skills_score'],
            'experience_score':      result['experience_score'],
            'education_score':       result['education_score'],
            'keywords_score':        result['keywords_score'],
            'total_score':           result['total_score'],
            'matched_skills':        result['matched_skills'],
            'missing_skills':        result['missing_skills'],
            'matched_keywords':      result['matched_keywords'],
            'experience_years_found': result['experience_years_found'],
            'education_rank_found':   result['education_rank_found'],
        },
    )
    return redirect('screening:result', pk=score.pk)


@login_required
def match_result(request, pk):
    """Show the detailed match score breakdown."""
    score = get_object_or_404(MatchScore, pk=pk)

    is_candidate = score.candidate == request.user
    is_owner = (
        _is_recruiter(request.user) and
        hasattr(request.user, 'recruiter_profile') and
        score.job.recruiter == request.user.recruiter_profile
    )
    if not is_candidate and not is_owner:
        messages.error(request, "Access denied.")
        return redirect('jobs:board')

    components = [
        {'label': 'Skills Match',      'score': score.skills_score,     'weight': 40, 'color': '#6366f1'},
        {'label': 'Experience',        'score': score.experience_score,  'weight': 25, 'color': '#10b981'},
        {'label': 'Education',         'score': score.education_score,   'weight': 15, 'color': '#f59e0b'},
        {'label': 'Keyword Relevance', 'score': score.keywords_score,    'weight': 20, 'color': '#3b82f6'},
    ]
    return render(request, 'screening/match_result.html', {
        'score': score,
        'job': score.job,
        'components': components,
    })


@login_required
def job_candidates(request, pk):
    """Recruiter view: ranked list of candidates who checked match."""
    if not _is_recruiter(request.user):
        messages.error(request, "Only recruiters can view candidates.")
        return redirect('jobs:board')

    job = get_object_or_404(JobPost, pk=pk)
    try:
        if job.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('jobs:manage')
    except Exception:
        return redirect('jobs:manage')

    scores = (MatchScore.objects
              .filter(job=job)
              .select_related('candidate')
              .order_by('-total_score'))

    return render(request, 'screening/candidates.html', {
        'job': job,
        'scores': scores,
    })


@login_required
@require_POST
def update_candidate_status(request, pk):
    """Recruiter updates a candidate's status and optional notes."""
    score = get_object_or_404(MatchScore, pk=pk)

    if not _is_recruiter(request.user):
        messages.error(request, "Access denied.")
        return redirect('screening:candidates', pk=score.job_id)

    try:
        if score.job.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('jobs:manage')
    except Exception:
        return redirect('jobs:manage')

    new_status = request.POST.get('status', '')
    valid = [c[0] for c in MatchScore.STATUS_CHOICES]
    if new_status in valid:
        score.status = new_status
        score.recruiter_notes = request.POST.get('notes', '').strip()
        score.save(update_fields=['status', 'recruiter_notes'])

    return redirect('screening:candidates', pk=score.job_id)


@login_required
def my_scores(request):
    """Job seeker view: history of all match scores."""
    if not _is_job_seeker(request.user):
        return redirect('jobs:board')

    scores = (MatchScore.objects
              .filter(candidate=request.user)
              .select_related('job', 'job__recruiter')
              .order_by('-computed_at'))

    return render(request, 'screening/my_scores.html', {
        'scores': scores,
    })


@login_required
def recruiter_screening(request):
    """Recruiter AI Screening overview — all jobs with candidate rankings."""
    if not _is_recruiter(request.user):
        messages.error(request, "Only recruiters can access the screening panel.")
        return redirect('jobs:board')

    try:
        recruiter_profile = request.user.recruiter_profile
    except Exception:
        messages.error(request, "Recruiter profile not found.")
        return redirect('accounts:dashboard')

    from django.db.models import Avg, Count, Max
    from applications.models import Application

    jobs = (JobPost.objects
            .filter(recruiter=recruiter_profile)
            .order_by('-created_at'))

    job_data = []
    total_scored = 0
    total_apps   = 0

    for job in jobs:
        scores_qs = MatchScore.objects.filter(job=job)
        apps_count = Application.objects.filter(job=job).count()
        scored_count = scores_qs.count()
        agg = scores_qs.aggregate(avg=Avg('total_score'), top=Max('total_score'))
        avg_score = round(agg['avg'] or 0, 1)
        top_score = round(agg['top'] or 0, 1)

        # Tier counts
        excellent = scores_qs.filter(total_score__gte=80).count()
        good      = scores_qs.filter(total_score__gte=60, total_score__lt=80).count()
        fair      = scores_qs.filter(total_score__gte=40, total_score__lt=60).count()
        low       = scores_qs.filter(total_score__lt=40).count()

        # Top 3 candidates
        top_candidates = (scores_qs
                          .select_related('candidate')
                          .order_by('-total_score')[:3])

        total_scored += scored_count
        total_apps   += apps_count

        job_data.append({
            'job':           job,
            'apps_count':    apps_count,
            'scored_count':  scored_count,
            'avg_score':     avg_score,
            'top_score':     top_score,
            'excellent':     excellent,
            'good':          good,
            'fair':          fair,
            'low':           low,
            'top_candidates': top_candidates,
        })

    return render(request, 'screening/recruiter_overview.html', {
        'profile':       recruiter_profile,
        'job_data':      job_data,
        'total_scored':  total_scored,
        'total_apps':    total_apps,
        'total_jobs':    len(job_data),
    })
