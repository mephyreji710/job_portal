from django.urls import path
from . import views

app_name = 'interviews'

urlpatterns = [
    # Recruiter
    path('applications/<int:application_pk>/schedule/', views.schedule_interview, name='schedule'),
    path('<int:pk>/cancel/',                             views.cancel_interview,   name='cancel'),

    # Job Seeker
    path('my/',                 views.my_interviews,    name='my_interviews'),
    path('<int:pk>/confirm/',   views.confirm_interview, name='confirm'),
    path('<int:pk>/decline/',   views.decline_interview, name='decline'),
]
