from collections import Counter
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from jobs.models import JobPost
from applications.models import Application
from interviews.models import Interview


def _is_admin(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'admin'


def _is_recruiter(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'recruiter'


def _parse_skills(jobs_qs):
    """Return Counter of skills from a queryset of JobPost objects."""
    counter = Counter()
    for skills_str in jobs_qs.exclude(required_skills='').values_list('required_skills', flat=True):
        for skill in skills_str.split(','):
            s = skill.strip()
            if s:
                counter[s.title()] += 1
    return counter


def _monthly_trend(apps_qs, months=6):
    """Return list of dicts {month_label, count} for last N months."""
    cutoff = timezone.now() - timedelta(days=months * 30)
    raw = (apps_qs
           .filter(applied_at__gte=cutoff)
           .annotate(month=TruncMonth('applied_at'))
           .values('month')
           .annotate(count=Count('id'))
           .order_by('month'))
    return [{'label': r['month'].strftime('%b %Y'), 'count': r['count']} for r in raw]


def _bar_pct(value, maximum):
    """Return integer percentage width for bar charts (min 2 if nonzero)."""
    if not maximum:
        return 0
    pct = round(value / maximum * 100)
    return max(pct, 2) if pct > 0 else 0


@login_required
def analytics_dashboard(request):
    """
    Admin  → platform-wide analytics.
    Recruiter → their company's analytics.
    """
    user = request.user

    if not (_is_admin(user) or _is_recruiter(user)):
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')

    # ── Scope ────────────────────────────────────────────────────────────
    if _is_admin(user):
        scope_label  = 'Platform-wide'
        jobs_qs      = JobPost.objects.all()
        apps_qs      = Application.objects.all()
        interviews_qs = Interview.objects.all()
    else:
        profile      = getattr(user, 'recruiter_profile', None)
        if not profile:
            messages.error(request, 'Recruiter profile not found.')
            return redirect('recruiter:panel')
        scope_label  = profile.company_name
        jobs_qs      = JobPost.objects.filter(recruiter=profile)
        apps_qs      = Application.objects.filter(job__recruiter=profile)
        interviews_qs = Interview.objects.filter(application__job__recruiter=profile)

    # ── Top-level counts ─────────────────────────────────────────────────
    total_jobs   = jobs_qs.count()
    active_jobs  = jobs_qs.filter(status=JobPost.STATUS_ACTIVE).count()
    total_apps   = apps_qs.count()
    total_hired  = apps_qs.filter(status='hired').count()

    # ── 1. Applications per Job (top 10) ─────────────────────────────────
    top_jobs = (jobs_qs
                .annotate(app_count=Count('applications'))
                .filter(app_count__gt=0)
                .order_by('-app_count')[:10])
    max_apps = top_jobs[0].app_count if top_jobs else 1
    apps_per_job = [
        {
            'title':   j.title,
            'company': j.recruiter.company_name,
            'count':   j.app_count,
            'pct':     _bar_pct(j.app_count, max_apps),
            'status':  j.status,
        }
        for j in top_jobs
    ]

    # ── 2. Hiring Rate (pipeline status breakdown) ───────────────────────
    status_counts = {
        'pending':     apps_qs.filter(status='pending').count(),
        'reviewed':    apps_qs.filter(status='reviewed').count(),
        'shortlisted': apps_qs.filter(status='shortlisted').count(),
        'rejected':    apps_qs.filter(status='rejected').count(),
        'hired':       apps_qs.filter(status='hired').count(),
    }
    # Build conic-gradient stops (degrees)
    def _pct(n): return round(n / total_apps * 100) if total_apps else 0
    pipeline = [
        {'label': 'Pending',     'count': status_counts['pending'],
         'pct': _pct(status_counts['pending']),     'color': '#94a3b8'},
        {'label': 'Reviewed',    'count': status_counts['reviewed'],
         'pct': _pct(status_counts['reviewed']),    'color': '#2563eb'},
        {'label': 'Shortlisted', 'count': status_counts['shortlisted'],
         'pct': _pct(status_counts['shortlisted']), 'color': '#10b981'},
        {'label': 'Rejected',    'count': status_counts['rejected'],
         'pct': _pct(status_counts['rejected']),    'color': '#ef4444'},
        {'label': 'Hired',       'count': status_counts['hired'],
         'pct': _pct(status_counts['hired']),       'color': '#8b5cf6'},
    ]
    # Build conic-gradient CSS string
    conic_stops = []
    cumulative = 0
    for p in pipeline:
        start = cumulative
        end   = cumulative + p['pct']
        if p['count'] > 0:
            conic_stops.append(f"{p['color']} {start}% {end}%")
        cumulative = end
    if cumulative < 100:
        conic_stops.append(f"#e5e7eb {cumulative}% 100%")
    donut_gradient = ', '.join(conic_stops) if conic_stops else '#e5e7eb 0% 100%'

    # ── 3. Most Demanded Skills (top 15) ─────────────────────────────────
    skill_counter = _parse_skills(jobs_qs)
    top_skills_raw = skill_counter.most_common(15)
    max_skill = top_skills_raw[0][1] if top_skills_raw else 1
    top_skills = [
        {'name': name, 'count': cnt, 'pct': _bar_pct(cnt, max_skill)}
        for name, cnt in top_skills_raw
    ]

    # ── 4. Monthly Applications Trend (last 6 months) ────────────────────
    monthly = _monthly_trend(apps_qs, months=6)
    max_monthly = max((m['count'] for m in monthly), default=1)
    for m in monthly:
        m['pct'] = _bar_pct(m['count'], max_monthly)

    # ── 5. Job Type Breakdown ─────────────────────────────────────────────
    type_counts = (jobs_qs
                   .values('job_type')
                   .annotate(count=Count('id'))
                   .order_by('-count'))
    type_labels = dict(JobPost.JOB_TYPE_CHOICES)
    max_type = type_counts[0]['count'] if type_counts else 1
    job_types = [
        {'label': type_labels.get(t['job_type'], t['job_type']),
         'count': t['count'],
         'pct':   _bar_pct(t['count'], max_type)}
        for t in type_counts
    ]

    # ── 6. Interview conversion ───────────────────────────────────────────
    interview_rate = round(interviews_qs.count() / total_apps * 100) if total_apps else 0
    hire_rate      = round(total_hired / total_apps * 100)           if total_apps else 0
    shortlist_rate = round(status_counts['shortlisted'] / total_apps * 100) if total_apps else 0

    context = {
        'scope_label':    scope_label,
        'is_admin':       _is_admin(user),
        'total_jobs':     total_jobs,
        'active_jobs':    active_jobs,
        'total_apps':     total_apps,
        'total_hired':    total_hired,
        'apps_per_job':   apps_per_job,
        'pipeline':       pipeline,
        'donut_gradient': donut_gradient,
        'top_skills':     top_skills,
        'monthly':        monthly,
        'job_types':      job_types,
        'interview_rate': interview_rate,
        'hire_rate':      hire_rate,
        'shortlist_rate': shortlist_rate,
    }
    return render(request, 'analytics/dashboard.html', context)
