from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('jobseeker/', include('jobseeker.urls', namespace='jobseeker')),
    path('resume/',     include('resume.urls',     namespace='resume')),
    path('recruiter/',  include('recruiter.urls',  namespace='recruiter')),
    path('jobs/',       include('jobs.urls',       namespace='jobs')),
    path('screening/',    include('screening.urls',    namespace='screening')),
    path('applications/', include('applications.urls', namespace='applications')),
    path('assessments/',  include('assessments.urls',  namespace='assessments')),
    path('interviews/',    include('interviews.urls',    namespace='interviews')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('analytics/',    include('analytics.urls',    namespace='analytics')),
    path('feedback/',     include('feedback.urls',     namespace='feedback')),
    path('tasks/',        include('tasks.urls',        namespace='tasks')),
    path('', lambda request: redirect('accounts:login'), name='home'),
    # Serve uploaded media files unconditionally (works regardless of DEBUG setting)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
