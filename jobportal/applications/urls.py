from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('jobs/<int:pk>/apply/',          views.apply,                     name='apply'),
    path('applications/<int:pk>/withdraw/', views.withdraw,                name='withdraw'),
    path('my-applications/',               views.my_applications,          name='my_applications'),
    path('jobs/<int:pk>/applicants/',      views.job_applicants,           name='applicants'),
    path('applications/<int:pk>/status/',  views.update_application_status, name='update_status'),
    path('all-applications/',             views.all_applications,          name='all_applications'),
    path('applications/<int:pk>/download/<str:resume_type>/', views.download_resume, name='download_resume'),
]
