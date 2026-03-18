from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings as django_settings

from applications.models import Application
from .models import Interview
from .forms import ScheduleInterviewForm
from notifications.utils import notify
from notifications.models import Notification


def _is_recruiter(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'recruiter'


def _is_job_seeker(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'job_seeker'


def _send_notification(subject, body, to_email):
    """Send a notification email (hits the console backend in dev)."""
    try:
        send_mail(
            subject,
            body,
            django_settings.DEFAULT_FROM_EMAIL if hasattr(django_settings, 'DEFAULT_FROM_EMAIL')
            else 'noreply@talentbridge.com',
            [to_email],
            fail_silently=True,
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Recruiter: Schedule an interview
# ---------------------------------------------------------------------------

@login_required
def schedule_interview(request, application_pk):
    """Create or update the interview for an application."""
    if not _is_recruiter(request.user):
        messages.error(request, "Only recruiters can schedule interviews.")
        return redirect('jobs:board')

    app = get_object_or_404(Application, pk=application_pk)
    try:
        if app.job.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('jobs:manage')
    except Exception:
        return redirect('jobs:manage')

    # Get existing interview or prepare new one
    existing = getattr(app, 'interview', None)
    is_edit = existing is not None

    if request.method == 'POST':
        form = ScheduleInterviewForm(request.POST, instance=existing)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = app
            interview.status = 'scheduled'
            interview.save()

            # Mark application as reviewed
            if app.status == 'pending':
                app.status = 'reviewed'
                app.save(update_fields=['status', 'updated_at'])

            # Email the candidate
            candidate = app.applicant
            subject = f"Interview Scheduled — {app.job.title} at {app.job.recruiter.company_name}"
            body = (
                f"Dear {candidate.get_full_name() or candidate.email},\n\n"
                f"Your interview has been scheduled for the position of {app.job.title} "
                f"at {app.job.recruiter.company_name}.\n\n"
                f"Date & Time : {interview.scheduled_at.strftime('%A, %B %d %Y at %I:%M %p')}\n"
                f"Duration    : {interview.duration_mins} minutes\n"
                f"Type        : {interview.get_interview_type_display()}\n"
            )
            if interview.location:
                body += f"Location    : {interview.location}\n"
            if interview.meeting_link:
                body += f"Meeting Link: {interview.meeting_link}\n"
            if interview.notes:
                body += f"\nNotes:\n{interview.notes}\n"
            body += "\nPlease log in to confirm or request a reschedule.\n\nBest regards,\nTalentBridge"
            _send_notification(subject, body, candidate.email)

            # In-app notification for the candidate
            action_word = "updated" if is_edit else "scheduled"
            notify(candidate, Notification.TYPE_INTERVIEW,
                   title=f'Interview {action_word}: {app.job.title}',
                   message=(f'{app.job.recruiter.company_name} has {action_word} a '
                            f'{interview.get_interview_type_display()} interview on '
                            f'{interview.scheduled_at.strftime("%b %d at %H:%M")}.'),
                   link='/interviews/my/',
                   from_user=request.user)

            action = "updated" if is_edit else "scheduled"
            messages.success(request, f"Interview {action} for {candidate.get_full_name() or candidate.email}.")
            return redirect('applications:applicants', pk=app.job_id)
    else:
        form = ScheduleInterviewForm(instance=existing)

    return render(request, 'interviews/schedule.html', {
        'form':    form,
        'app':     app,
        'is_edit': is_edit,
        'existing': existing,
    })


# ---------------------------------------------------------------------------
# Recruiter: Cancel interview
# ---------------------------------------------------------------------------

@login_required
@require_POST
def cancel_interview(request, pk):
    interview = get_object_or_404(Interview, pk=pk)
    try:
        if interview.application.job.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('jobs:manage')
    except Exception:
        return redirect('jobs:manage')

    interview.status = 'cancelled'
    interview.save(update_fields=['status', 'updated_at'])

    candidate = interview.application.applicant
    subject = f"Interview Cancelled — {interview.application.job.title}"
    body = (
        f"Dear {candidate.get_full_name() or candidate.email},\n\n"
        f"We regret to inform you that your interview for {interview.application.job.title} "
        f"at {interview.application.job.recruiter.company_name} has been cancelled.\n\n"
        f"The recruiter may reschedule. Please check your TalentBridge account for updates.\n\n"
        f"Best regards,\nTalentBridge"
    )
    _send_notification(subject, body, candidate.email)
    notify(candidate, Notification.TYPE_INTERVIEW_CANCEL,
           title=f'Interview cancelled: {interview.application.job.title}',
           message=f'{interview.application.job.recruiter.company_name} cancelled your interview.',
           link='/interviews/my/',
           from_user=request.user)
    messages.success(request, "Interview cancelled and candidate notified.")
    return redirect('applications:applicants', pk=interview.application.job_id)


# ---------------------------------------------------------------------------
# Job Seeker: My Interviews
# ---------------------------------------------------------------------------

@login_required
def my_interviews(request):
    if not _is_job_seeker(request.user):
        return redirect('jobs:board')

    interviews = (Interview.objects
                  .filter(application__applicant=request.user)
                  .select_related('application__job', 'application__job__recruiter')
                  .order_by('scheduled_at'))

    upcoming   = interviews.exclude(status='cancelled').exclude(status='completed')
    past       = interviews.filter(status__in=['completed', 'cancelled'])

    return render(request, 'interviews/my_interviews.html', {
        'upcoming': upcoming,
        'past':     past,
        'total':    interviews.count(),
    })


# ---------------------------------------------------------------------------
# Job Seeker: Confirm interview
# ---------------------------------------------------------------------------

@login_required
@require_POST
def confirm_interview(request, pk):
    interview = get_object_or_404(
        Interview, pk=pk, application__applicant=request.user)

    interview.status = 'confirmed'
    interview.save(update_fields=['status', 'updated_at'])

    # Notify recruiter
    recruiter_user = interview.application.job.recruiter.user
    subject = f"Interview Confirmed — {interview.application.applicant.get_full_name() or interview.application.applicant.email}"
    body = (
        f"{interview.application.applicant.get_full_name() or interview.application.applicant.email} "
        f"has confirmed their interview for {interview.application.job.title} "
        f"on {interview.scheduled_at.strftime('%A, %B %d %Y at %I:%M %p')}."
    )
    _send_notification(subject, body, recruiter_user.email)
    notify(recruiter_user, Notification.TYPE_INTERVIEW_CONFIRM,
           title=f'Interview confirmed by {interview.application.applicant.get_full_name() or interview.application.applicant.email}',
           message=f'For {interview.application.job.title} on {interview.scheduled_at.strftime("%b %d at %H:%M")}.',
           link=f'/applications/jobs/{interview.application.job_id}/applicants/',
           from_user=request.user)
    messages.success(request, "Interview confirmed! We've notified the recruiter.")
    return redirect('interviews:my_interviews')


# ---------------------------------------------------------------------------
# Job Seeker: Decline / request reschedule
# ---------------------------------------------------------------------------

@login_required
@require_POST
def decline_interview(request, pk):
    interview = get_object_or_404(
        Interview, pk=pk, application__applicant=request.user)

    interview.status = 'cancelled'
    interview.save(update_fields=['status', 'updated_at'])

    recruiter_user = interview.application.job.recruiter.user
    subject = f"Interview Declined — {interview.application.applicant.get_full_name() or interview.application.applicant.email}"
    body = (
        f"{interview.application.applicant.get_full_name() or interview.application.applicant.email} "
        f"has declined the interview for {interview.application.job.title}. "
        f"Please log in to reschedule."
    )
    _send_notification(subject, body, recruiter_user.email)
    notify(recruiter_user, Notification.TYPE_INTERVIEW_CANCEL,
           title=f'Interview declined: {interview.application.job.title}',
           message=f'{interview.application.applicant.get_full_name() or interview.application.applicant.email} declined the interview.',
           link=f'/applications/jobs/{interview.application.job_id}/applicants/',
           from_user=request.user)
    messages.info(request, "Interview declined. The recruiter has been notified.")
    return redirect('interviews:my_interviews')
