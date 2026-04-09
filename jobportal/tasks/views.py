from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone

from applications.models import Application
from notifications.utils import notify
from notifications.models import Notification
from .models import Task, TaskSubmission
from .forms import AssignTaskForm, TaskSubmissionForm, ReviewTaskForm


def _is_job_seeker(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'job_seeker'


def _is_recruiter(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'recruiter'


# ---------------------------------------------------------------------------
# Recruiter: Assign Task to Applicant
# ---------------------------------------------------------------------------

@login_required
def assign_task(request, application_id):
    if not _is_recruiter(request.user):
        messages.error(request, "Only recruiters can assign tasks.")
        return redirect('accounts:dashboard')

    app = get_object_or_404(Application, pk=application_id)

    try:
        recruiter_profile = request.user.recruiter_profile
        if app.job.recruiter != recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('jobs:manage')
    except Exception:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = AssignTaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.application = app
            task.recruiter   = recruiter_profile
            task.save()

            # Notify the seeker
            company = recruiter_profile.company_name
            notify(
                app.applicant,
                Notification.TYPE_ASSESSMENT,
                title=f'New task assigned: {task.title}',
                message=f'{company} has assigned you a task for {app.job.title}.',
                link='/tasks/',
                from_user=request.user,
            )

            messages.success(request, f'Task "{task.title}" assigned to {app.applicant.get_full_name() or app.applicant.email}.')
            return redirect('applications:applicants', pk=app.job_id)
    else:
        form = AssignTaskForm()

    return render(request, 'tasks/assign_task.html', {
        'form': form,
        'app':  app,
    })


# ---------------------------------------------------------------------------
# Recruiter: All Assigned Tasks
# ---------------------------------------------------------------------------

@login_required
def recruiter_tasks(request):
    if not _is_recruiter(request.user):
        messages.error(request, "Only recruiters can view this page.")
        return redirect('accounts:dashboard')

    try:
        recruiter_profile = request.user.recruiter_profile
    except Exception:
        return redirect('accounts:dashboard')

    status_filter = request.GET.get('status', '')
    tasks_qs = Task.objects.filter(recruiter=recruiter_profile).select_related(
        'application', 'application__applicant', 'application__job'
    )
    if status_filter:
        tasks_qs = tasks_qs.filter(status=status_filter)

    counts = {
        'total':       Task.objects.filter(recruiter=recruiter_profile).count(),
        'pending':     Task.objects.filter(recruiter=recruiter_profile, status='pending').count(),
        'in_progress': Task.objects.filter(recruiter=recruiter_profile, status='in_progress').count(),
        'submitted':   Task.objects.filter(recruiter=recruiter_profile, status='submitted').count(),
        'approved':    Task.objects.filter(recruiter=recruiter_profile, status='approved').count(),
        'rejected':    Task.objects.filter(recruiter=recruiter_profile, status='rejected').count(),
    }

    return render(request, 'tasks/recruiter_tasks.html', {
        'tasks':         tasks_qs,
        'counts':        counts,
        'status_filter': status_filter,
    })


# ---------------------------------------------------------------------------
# Recruiter: Review a Submitted Task
# ---------------------------------------------------------------------------

@login_required
def review_task(request, pk):
    if not _is_recruiter(request.user):
        messages.error(request, "Only recruiters can review tasks.")
        return redirect('accounts:dashboard')

    task = get_object_or_404(Task, pk=pk)

    try:
        if task.recruiter != request.user.recruiter_profile:
            messages.error(request, "Access denied.")
            return redirect('tasks:recruiter_tasks')
    except Exception:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = ReviewTaskForm(request.POST)
        if form.is_valid():
            action   = form.cleaned_data['action']
            feedback = form.cleaned_data['feedback']

            task.status = action
            task.save(update_fields=['status', 'updated_at'])

            if hasattr(task, 'submission'):
                task.submission.recruiter_feedback = feedback
                task.submission.reviewed_at = timezone.now()
                task.submission.save(update_fields=['recruiter_feedback', 'reviewed_at'])

            # Notify seeker
            company = task.recruiter.company_name
            if action == 'approved':
                notify(
                    task.application.applicant,
                    Notification.TYPE_HIRED,
                    title=f'Task approved: {task.title}',
                    message=f'{company} has approved your task submission.',
                    link='/tasks/',
                    from_user=request.user,
                )
                messages.success(request, "Task submission approved.")
            else:
                notify(
                    task.application.applicant,
                    Notification.TYPE_REJECTED,
                    title=f'Task needs revision: {task.title}',
                    message=f'{company} has reviewed your task and sent feedback.',
                    link='/tasks/',
                    from_user=request.user,
                )
                messages.warning(request, "Task submission rejected with feedback.")

            return redirect('tasks:recruiter_tasks')
    else:
        form = ReviewTaskForm()

    return render(request, 'tasks/review_task.html', {
        'task': task,
        'form': form,
    })


# ---------------------------------------------------------------------------
# Job Seeker: My Tasks
# ---------------------------------------------------------------------------

@login_required
def my_tasks(request):
    if not _is_job_seeker(request.user):
        messages.error(request, "Only job seekers can view their tasks.")
        return redirect('accounts:dashboard')

    status_filter = request.GET.get('status', '')
    tasks_qs = Task.objects.filter(
        application__applicant=request.user
    ).select_related('recruiter', 'application__job')

    if status_filter:
        tasks_qs = tasks_qs.filter(status=status_filter)

    counts = {
        'total':       Task.objects.filter(application__applicant=request.user).count(),
        'pending':     Task.objects.filter(application__applicant=request.user, status='pending').count(),
        'in_progress': Task.objects.filter(application__applicant=request.user, status='in_progress').count(),
        'submitted':   Task.objects.filter(application__applicant=request.user, status='submitted').count(),
        'approved':    Task.objects.filter(application__applicant=request.user, status='approved').count(),
        'rejected':    Task.objects.filter(application__applicant=request.user, status='rejected').count(),
    }

    return render(request, 'tasks/my_tasks.html', {
        'tasks':         tasks_qs,
        'counts':        counts,
        'status_filter': status_filter,
    })


# ---------------------------------------------------------------------------
# Job Seeker: Task Detail + Submit Work
# ---------------------------------------------------------------------------

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, application__applicant=request.user)

    # Auto-progress from pending to in_progress on first view
    if task.status == Task.STATUS_PENDING:
        task.status = Task.STATUS_INPROGRESS
        task.save(update_fields=['status', 'updated_at'])

    try:
        submission = task.submission
    except TaskSubmission.DoesNotExist:
        submission = None

    if request.method == 'POST':
        if task.status in (Task.STATUS_APPROVED, Task.STATUS_SUBMITTED):
            messages.info(request, "This task has already been submitted or approved.")
            return redirect('tasks:task_detail', pk=pk)

        form = TaskSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.task = task
            sub.save()

            task.status = Task.STATUS_SUBMITTED
            task.save(update_fields=['status', 'updated_at'])

            # Notify recruiter
            seeker_name = request.user.get_full_name() or request.user.email
            notify(
                task.recruiter.user,
                Notification.TYPE_DOCS_SUBMITTED,
                title=f'Task submitted: {task.title}',
                message=f'{seeker_name} has submitted their task.',
                link='/tasks/recruiter/',
                from_user=request.user,
            )

            messages.success(request, "Task submitted successfully!")
            return redirect('tasks:task_detail', pk=pk)
    else:
        form = TaskSubmissionForm(instance=submission)

    return render(request, 'tasks/task_detail.html', {
        'task':       task,
        'submission': submission,
        'form':       form,
    })


# ---------------------------------------------------------------------------
# Seeker: Update Task Status (start/mark in progress)
# ---------------------------------------------------------------------------

@login_required
@require_POST
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk, application__applicant=request.user)
    new_status = request.POST.get('status', '')

    # Seekers may only move between pending ↔ in_progress (not submitted/approved/rejected)
    allowed = {
        Task.STATUS_PENDING:    [Task.STATUS_INPROGRESS],
        Task.STATUS_INPROGRESS: [Task.STATUS_PENDING],
    }
    if new_status in allowed.get(task.status, []):
        task.status = new_status
        task.save(update_fields=['status', 'updated_at'])

    return redirect('tasks:my_tasks')
