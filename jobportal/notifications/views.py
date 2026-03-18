from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notifications_list(request):
    notifs = (Notification.objects
              .filter(user=request.user)
              .select_related('from_user'))
    notifs.filter(is_read=False).update(is_read=True)

    role = getattr(request.user, 'role', None)
    ctx  = {'notifications': notifs}

    if role == 'recruiter':
        try:
            ctx['profile'] = request.user.recruiter_profile
        except Exception:
            pass
        ctx['base_template'] = 'recruiter/base_recruiter.html'
    else:
        try:
            from jobseeker.models import JobSeekerProfile
            ctx['profile'], _ = JobSeekerProfile.objects.get_or_create(user=request.user)
        except Exception:
            pass
        ctx['base_template'] = 'jobseeker/base_profile.html'

    return render(request, 'notifications/list.html', ctx)


@login_required
@require_POST
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    if notif.link:
        return redirect(notif.link)
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications:list')
