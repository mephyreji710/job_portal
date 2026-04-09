from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

from .forms import (
    JobSeekerRegistrationForm,
    RecruiterRegistrationForm,
    LoginForm,
    PasswordResetRequestForm,
    SetNewPasswordForm,
)
from .models import User

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _send_verification_email(user, request):
    from django.contrib.auth.tokens import default_token_generator
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    verify_url = f'{site_url}/accounts/verify-email/{uid}/{token}/'
    subject = 'Verify your TalentBridge email address'
    message = render_to_string('accounts/email/verify_email.html', {
        'user': user,
        'verify_url': verify_url,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message)


def _send_password_reset_email(user, request):
    from django.contrib.auth.tokens import default_token_generator
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    reset_url = f'{site_url}/accounts/password-reset/confirm/{uid}/{token}/'
    subject = 'Reset your TalentBridge password'
    message = render_to_string('accounts/email/reset_password.html', {
        'user': user,
        'reset_url': reset_url,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message)


def _role_redirect(user):
    """Return the correct dashboard redirect after login."""
    if user.is_admin_user():
        return redirect('accounts:admin_dashboard')
    elif user.is_recruiter_user():
        return redirect('accounts:recruiter_dashboard')
    else:
        return redirect('accounts:jobseeker_dashboard')


# ---------------------------------------------------------------------------
# Login / Logout
# ---------------------------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return _role_redirect(request.user)

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        remember_me = form.cleaned_data.get('remember_me', False)

        user = authenticate(request, username=email, password=password)
        if user is None:
            # Check if account exists but is unverified
            try:
                unverified = User.objects.get(email__iexact=email, is_active=False)
                if unverified.check_password(password):
                    messages.warning(request,
                        'Your email address is not verified yet. '
                        'Please check your inbox and click the verification link.')
                else:
                    messages.error(request, 'Invalid email or password. Please try again.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password. Please try again.')
        else:
            login(request, user, backend='accounts.backends.EmailBackend')
            if not remember_me:
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return _role_redirect(user)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_role_select(request):
    if request.user.is_authenticated:
        return _role_redirect(request.user)
    return render(request, 'accounts/register_role_select.html')


def register_jobseeker(request):
    if request.user.is_authenticated:
        return _role_redirect(request.user)

    form = JobSeekerRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False   # require email verification
        user.save()
        form.save_m2m()
        _send_verification_email(user, request)
        return redirect('accounts:registration_pending')

    return render(request, 'accounts/register_jobseeker.html', {'form': form})


def register_recruiter(request):
    if request.user.is_authenticated:
        return _role_redirect(request.user)

    form = RecruiterRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False   # require email verification
        user.save()
        form.save_m2m()
        _send_verification_email(user, request)
        return redirect('accounts:registration_pending')

    return render(request, 'accounts/register_recruiter.html', {'form': form})


# ---------------------------------------------------------------------------
# Password Reset
# ---------------------------------------------------------------------------

def password_reset_request(request):
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            _send_password_reset_email(user, request)
        except User.DoesNotExist:
            pass  # Silently ignore unknown emails
        return redirect('accounts:password_reset_done')

    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    from django.contrib.auth.tokens import default_token_generator

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    token_valid = user is not None and default_token_generator.check_token(user, token)

    if not token_valid:
        return render(request, 'accounts/password_reset_confirm.html', {'invalid': True})

    form = SetNewPasswordForm(user=user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Password reset successful! You can now log in.')
        return redirect('accounts:password_reset_complete')

    return render(request, 'accounts/password_reset_confirm.html', {'form': form, 'invalid': False})


def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')


# ---------------------------------------------------------------------------
# Email Verification
# ---------------------------------------------------------------------------

def registration_pending(request):
    """Shown after registration — tells user to check their email."""
    return render(request, 'accounts/registration_pending.html')


def verify_email(request, uidb64, token):
    from django.contrib.auth.tokens import default_token_generator
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and not user.is_active and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])
        login(request, user, backend='accounts.backends.EmailBackend')
        messages.success(request, f'Email verified! Welcome to TalentBridge, {user.first_name or user.username}!')
        return render(request, 'accounts/email_verified.html', {'user': user, 'valid': True})

    return render(request, 'accounts/email_verified.html', {'valid': False})


def resend_verification(request):
    """POST: resend the verification email for an unverified address."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email__iexact=email, is_active=False)
            _send_verification_email(user, request)
        except User.DoesNotExist:
            pass  # Silently ignore — don't leak whether email exists
        messages.success(request, 'Verification email resent! Please check your inbox.')
    return redirect('accounts:registration_pending')


# ---------------------------------------------------------------------------
# Dashboards
# ---------------------------------------------------------------------------

@login_required(login_url='/accounts/login/')
def dashboard_redirect(request):
    return _role_redirect(request.user)


@login_required(login_url='/accounts/login/')
def admin_dashboard(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return _role_redirect(request.user)
    from django.utils import timezone
    from datetime import timedelta
    from jobs.models import JobPost
    from applications.models import Application
    from interviews.models import Interview
    from accounts.models import RecruiterProfile

    now       = timezone.now()
    week_ago  = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Users
    total_users     = User.objects.count()
    total_rec       = User.objects.filter(role=User.RECRUITER).count()
    total_js        = User.objects.filter(role=User.JOB_SEEKER).count()
    new_this_week   = User.objects.filter(date_joined__gte=week_ago).count()
    new_this_month  = User.objects.filter(date_joined__gte=month_ago).count()
    # Jobs
    total_jobs      = JobPost.objects.count()
    active_jobs     = JobPost.objects.filter(status=JobPost.STATUS_ACTIVE).count()
    jobs_this_month = JobPost.objects.filter(created_at__gte=month_ago).count()
    # Active recruiters = those with at least one active job
    active_recruiters = RecruiterProfile.objects.filter(
        jobs__status=JobPost.STATUS_ACTIVE
    ).distinct().count()
    # Hiring pipeline
    total_apps    = Application.objects.count()
    pending_apps  = Application.objects.filter(status='pending').count()
    reviewed_apps = Application.objects.filter(status='reviewed').count()
    shortlisted   = Application.objects.filter(status='shortlisted').count()
    rejected      = Application.objects.filter(status='rejected').count()
    hired         = Application.objects.filter(status='hired').count()
    # Interviews
    total_interviews     = Interview.objects.count()
    upcoming_interviews  = Interview.objects.filter(
        scheduled_at__gte=now).exclude(status__in=['cancelled', 'completed']).count()
    confirmed_interviews = Interview.objects.filter(status='confirmed').count()
    # Recent
    recent_users = User.objects.order_by('-date_joined')[:8]
    recent_jobs  = JobPost.objects.select_related('recruiter').order_by('-created_at')[:5]

    stats = {
        'total_users':    total_users,    'recruiters':    total_rec,
        'job_seekers':    total_js,       'new_this_week': new_this_week,
        'new_this_month': new_this_month,
        'total_jobs':     total_jobs,     'active_jobs':   active_jobs,
        'jobs_this_month': jobs_this_month,
        'active_recruiters': active_recruiters,
        'total_apps':    total_apps,      'pending_apps':  pending_apps,
        'reviewed_apps': reviewed_apps,   'shortlisted':   shortlisted,
        'rejected':      rejected,        'hired':         hired,
        'total_interviews':    total_interviews,
        'upcoming_interviews': upcoming_interviews,
        'confirmed_interviews': confirmed_interviews,
        'recent_users': recent_users,
        'recent_jobs':  recent_jobs,
    }
    return render(request, 'accounts/admin_dashboard.html', {'stats': stats})


@login_required(login_url='/accounts/login/')
def admin_user_list(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return _role_redirect(request.user)

    qs = User.objects.all().order_by('-date_joined')
    search = request.GET.get('q', '').strip()
    role   = request.GET.get('role', '').strip()
    if search:
        from django.db.models import Q
        qs = qs.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    if role in (User.ADMIN, User.RECRUITER, User.JOB_SEEKER):
        qs = qs.filter(role=role)

    from django.core.paginator import Paginator
    paginator = Paginator(qs, 20)
    page      = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'accounts/admin_users.html', {
        'page_obj': page,
        'search':   search,
        'role':     role,
        'total':    qs.count(),
    })


@login_required(login_url='/accounts/login/')
def admin_delete_user(request, pk):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return _role_redirect(request.user)
    if request.method != 'POST':
        return redirect('accounts:admin_user_list')

    target = get_object_or_404(User, pk=pk)
    if target.pk == request.user.pk:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('accounts:admin_user_list')
    if target.is_admin_user():
        messages.error(request, 'Admin accounts cannot be deleted here.')
        return redirect('accounts:admin_user_list')

    name = target.get_full_name() or target.email
    target.delete()
    messages.success(request, f'User "{name}" has been deleted.')
    return redirect('accounts:admin_user_list')


@login_required(login_url='/accounts/login/')
def recruiter_dashboard(request):
    if not request.user.is_recruiter_user():
        messages.error(request, 'Access denied.')
        return _role_redirect(request.user)
    profile = getattr(request.user, 'recruiter_profile', None)

    from jobs.models import JobPost
    from applications.models import Application
    from interviews.models import Interview
    from django.utils import timezone

    active_jobs = 0
    total_applications = 0
    shortlisted = 0
    upcoming_interviews = 0

    if profile:
        job_ids = list(profile.jobs.values_list('id', flat=True))
        active_jobs = profile.jobs.filter(status=JobPost.STATUS_ACTIVE).count()
        total_applications = Application.objects.filter(job__in=job_ids).count()
        shortlisted = Application.objects.filter(job__in=job_ids, status='shortlisted').count()
        upcoming_interviews = Interview.objects.filter(
            application__job__in=job_ids,
            scheduled_at__gte=timezone.now(),
        ).exclude(status__in=['cancelled', 'completed']).count()

    return render(request, 'accounts/recruiter_dashboard.html', {
        'profile':             profile,
        'active_jobs':         active_jobs,
        'total_applications':  total_applications,
        'shortlisted':         shortlisted,
        'upcoming_interviews': upcoming_interviews,
    })


@login_required(login_url='/accounts/login/')
def jobseeker_dashboard(request):
    if not request.user.is_job_seeker_user():
        messages.error(request, 'Access denied.')
        return _role_redirect(request.user)
    profile = getattr(request.user, 'js_profile', None)
    skills_list = list(profile.skills.all()) if profile else []
    from applications.models import Application
    from jobs.models import SavedJob
    from interviews.models import Interview
    from django.utils import timezone
    applied_count = Application.objects.filter(applicant=request.user).count()
    saved_count   = SavedJob.objects.filter(user=request.user).count()
    upcoming_interviews = Interview.objects.filter(
        application__applicant=request.user,
        scheduled_at__gte=timezone.now(),
    ).exclude(status__in=['cancelled', 'completed']).count()
    return render(request, 'accounts/jobseeker_dashboard.html', {
        'profile':             profile,
        'skills_list':         skills_list,
        'applied_count':       applied_count,
        'saved_count':         saved_count,
        'upcoming_interviews': upcoming_interviews,
    })
