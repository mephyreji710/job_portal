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
]
