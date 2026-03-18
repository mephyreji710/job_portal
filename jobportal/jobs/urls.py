from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Public
    path('',                         views.job_board,            name='board'),
    path('<int:pk>/',                views.job_detail,           name='detail'),

    # Recruiter management
    path('manage/',                  views.manage,               name='manage'),
    path('new/',                     views.job_new,              name='new'),
    path('<int:pk>/edit/',           views.job_edit,             name='edit'),
    path('<int:pk>/delete/',         views.job_delete,           name='delete'),
    path('<int:pk>/status/',         views.job_toggle_status,    name='toggle_status'),
    path('<int:pk>/preview/',        views.job_detail_recruiter, name='preview'),

    # Job Seeker: save/wishlist
    path('<int:pk>/save/',           views.toggle_save,          name='save'),
    path('saved/',                   views.saved_jobs,           name='saved'),
]
