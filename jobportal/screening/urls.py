from django.urls import path
from . import views

app_name = 'screening'

urlpatterns = [
    path('match/<int:pk>/check/',      views.check_match,          name='check'),
    path('match/<int:pk>/result/',     views.match_result,         name='result'),
    path('jobs/<int:pk>/candidates/',  views.job_candidates,       name='candidates'),
    path('match/<int:pk>/status/',     views.update_candidate_status, name='update_status'),
    path('my-scores/',                 views.my_scores,            name='my_scores'),
    path('recruiter/',                 views.recruiter_screening,  name='recruiter_overview'),
]
