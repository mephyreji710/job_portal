from django.urls import path
from . import views

app_name = 'jobseeker'

urlpatterns = [
    # Profile overview
    path('profile/',                            views.profile_view,          name='profile'),
    path('profile/edit/',                       views.personal_edit,         name='personal_edit'),

    # Skills
    path('profile/skills/',                     views.skills_manage,         name='skills'),
    path('profile/skills/<int:pk>/delete/',     views.skill_delete,          name='skill_delete'),

    # Education
    path('profile/education/',                  views.education_manage,      name='education'),
    path('profile/education/add/',              views.education_add,         name='education_add'),
    path('profile/education/<int:pk>/edit/',    views.education_edit,        name='education_edit'),
    path('profile/education/<int:pk>/delete/',  views.education_delete,      name='education_delete'),

    # Experience
    path('profile/experience/',                 views.experience_manage,     name='experience'),
    path('profile/experience/add/',             views.experience_add,        name='experience_add'),
    path('profile/experience/<int:pk>/edit/',   views.experience_edit,       name='experience_edit'),
    path('profile/experience/<int:pk>/delete/', views.experience_delete,     name='experience_delete'),

    # Certifications
    path('profile/certifications/',                     views.certifications_manage, name='certifications'),
    path('profile/certifications/add/',                 views.certification_add,     name='certification_add'),
    path('profile/certifications/<int:pk>/edit/',       views.certification_edit,    name='certification_edit'),
    path('profile/certifications/<int:pk>/delete/',     views.certification_delete,  name='certification_delete'),
]
