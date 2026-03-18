from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count

from applications.models import Application
from accounts.models import RecruiterProfile
from notifications.utils import notify
from notifications.models import Notification
from .models import Feedback
from .forms import FeedbackForm


def _is_job_seeker(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'job_seeker'


def _is_recruiter(user):
    return user.is_authenticated and getattr(user, 'role', None) == 'recruiter'


@login_required
def give_feedback(request, application_pk):
    app = get_object_or_404(Application, pk=application_pk)
    user = request.user

    if _is_job_seeker(user):
        if app.applicant != user:
            messages.error(request, 'Access denied.')
            return redirect('applications:my_applications')
        if app.status == 'pending':
            messages.error(request, 'You can rate a company after your application has been reviewed.')
            return redirect('applications:my_applications')
        feedback_type = Feedback.TYPE_C2CO
        target_name   = app.job.recruiter.company_name
        redirect_url  = 'applications:my_applications'
        redirect_args = []

    elif _is_recruiter(user):
        try:
            if app.job.recruiter != user.recruiter_profile:
                messages.error(request, 'Access denied.')
                return redirect('jobs:manage')
        except Exception:
            return redirect('jobs:manage')
        if app.status == 'pending':
            messages.error(request, 'Review the application before rating the candidate.')
            return redirect('applications:applicants', pk=app.job_id)
        feedback_type = Feedback.TYPE_CO2C
        target_name   = app.applicant.get_full_name() or app.applicant.email
        redirect_url  = 'applications:applicants'
        redirect_args = [app.job_id]
    else:
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')

    existing = Feedback.objects.filter(application=app, feedback_type=feedback_type).first()
    if existing:
        messages.info(request, 'You have already submitted feedback for this application.')
        return redirect(redirect_url, *redirect_args) if redirect_args else redirect(redirect_url)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.application   = app
            fb.from_user     = user
            fb.feedback_type = feedback_type
            fb.save()

            if feedback_type == Feedback.TYPE_C2CO:
                recruiter_user = app.job.recruiter.user
                notify(recruiter_user, Notification.TYPE_APP_RECEIVED,
                       title='New company review received',
                       message=f'{fb.rating} stars for {app.job.title}.',
                       link=f'/feedback/company/{app.job.recruiter_id}/reviews/')
            else:
                notify(app.applicant, Notification.TYPE_SHORTLISTED,
                       title=f'Feedback from {app.job.recruiter.company_name}',
                       message=f'{fb.rating} stars for your application to {app.job.title}.',
                       link='/feedback/my-ratings/')

            messages.success(request, f'Feedback for {target_name} submitted. Thank you!')
            return redirect(redirect_url, *redirect_args) if redirect_args else redirect(redirect_url)
    else:
        form = FeedbackForm()

    return render(request, 'feedback/give.html', {
        'form':          form,
        'app':           app,
        'feedback_type': feedback_type,
        'target_name':   target_name,
        'is_c2co':       feedback_type == Feedback.TYPE_C2CO,
    })


def company_reviews(request, profile_pk):
    profile = get_object_or_404(RecruiterProfile, pk=profile_pk)
    reviews = (Feedback.objects
               .filter(application__job__recruiter=profile, feedback_type=Feedback.TYPE_C2CO)
               .select_related('from_user', 'application__job')
               .order_by('-created_at'))

    agg           = reviews.aggregate(avg=Avg('rating'), total=Count('id'))
    avg_rating    = round(agg['avg'], 1) if agg['avg'] else None
    total_reviews = agg['total']

    breakdown = {}
    for i in range(1, 6):
        cnt = reviews.filter(rating=i).count()
        breakdown[i] = {'count': cnt, 'pct': round(cnt / total_reviews * 100) if total_reviews else 0}

    return render(request, 'feedback/company_reviews.html', {
        'profile': profile, 'reviews': reviews,
        'avg_rating': avg_rating, 'total_reviews': total_reviews,
        'breakdown': breakdown,
    })


@login_required
def my_ratings(request):
    if not _is_job_seeker(request.user):
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')

    ratings = (Feedback.objects
               .filter(application__applicant=request.user, feedback_type=Feedback.TYPE_CO2C)
               .select_related('application__job', 'application__job__recruiter')
               .order_by('-created_at'))

    agg           = ratings.aggregate(avg=Avg('rating'), total=Count('id'))
    avg_rating    = round(agg['avg'], 1) if agg['avg'] else None
    total_ratings = agg['total']

    return render(request, 'feedback/my_ratings.html', {
        'ratings': ratings, 'avg_rating': avg_rating, 'total_ratings': total_ratings,
    })
