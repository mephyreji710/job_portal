from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Seeker
    path('',                         views.my_tasks,           name='my_tasks'),
    path('<int:pk>/',                views.task_detail,        name='task_detail'),
    path('<int:pk>/status/',         views.update_task_status, name='update_status'),

    # Recruiter
    path('recruiter/',               views.recruiter_tasks,    name='recruiter_tasks'),
    path('assign/<int:application_id>/', views.assign_task,   name='assign_task'),
    path('<int:pk>/review/',         views.review_task,        name='review_task'),
]
