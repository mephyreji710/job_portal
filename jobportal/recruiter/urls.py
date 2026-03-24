from django.urls import path
from . import views

app_name = 'recruiter'

urlpatterns = [
    path('',                          views.company_panel,   name='panel'),
    path('edit/',                     views.edit_profile,    name='edit'),
    path('team/',                     views.hr_team,         name='team'),
    path('team/add/',                 views.add_hr_member,   name='add_hr_member'),
    path('team/remove/<int:pk>/',     views.remove_hr_member, name='remove_hr_member'),
    path('jobs/',                     views.jobs_list,       name='jobs'),
    path('company/<int:pk>/',         views.public_company_profile, name='public_profile'),
]
