from django.urls import path
from . import views

app_name = 'resume'

urlpatterns = [
    path('',                          views.resume_list,      name='list'),
    path('upload/',                   views.upload,           name='upload'),
    path('<int:pk>/',                 views.detail,           name='detail'),
    path('<int:pk>/delete/',          views.delete,           name='delete'),
    path('<int:pk>/reparse/',         views.reparse,          name='reparse'),
    path('<int:pk>/set-primary/',     views.set_primary,      name='set_primary'),
    path('<int:pk>/apply-to-profile/', views.apply_to_profile, name='apply_to_profile'),
    # Resume Builder
    path('builder/',                    views.builder_list,    name='builder_list'),
    path('builder/new/',                views.builder_create,  name='builder_create'),
    path('builder/<int:pk>/edit/',      views.builder_edit,    name='builder_edit'),
    path('builder/<int:pk>/preview/',   views.builder_preview, name='builder_preview'),
    path('builder/<int:pk>/delete/',    views.builder_delete,  name='builder_delete'),
]
