from django.urls import path
from . import views

app_name = 'assessment'

urlpatterns = [
    path('job/<int:job_pk>/manage/',       views.manage_assessment, name='manage'),
    path('send/<int:app_pk>/',             views.send_assessment,   name='send'),
    path('result/<int:attempt_pk>/',       views.attempt_detail,    name='detail'),
    path('take/<int:attempt_pk>/',         views.take_assessment,   name='take'),
    path('my-result/<int:attempt_pk>/',    views.attempt_result,    name='my_result'),
]
