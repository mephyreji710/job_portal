from django.urls import path
from . import views

app_name = 'recruiter'

urlpatterns = [
    path('',          views.company_panel, name='panel'),
    path('edit/',     views.edit_profile,  name='edit'),
    path('team/',     views.hr_team,       name='team'),
    path('jobs/',     views.jobs_list,     name='jobs'),
]
