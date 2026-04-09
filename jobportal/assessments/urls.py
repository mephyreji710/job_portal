from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('create/<int:application_pk>/',              views.create_assessment, name='create'),
    path('<int:pk>/take/',                            views.take_assessment,   name='take'),
    path('result/<int:pk>/',                          views.assessment_result, name='result'),
    path('<int:pk>/recruiter-result/',                views.recruiter_result,  name='recruiter_result'),
    path('<int:pk>/request-docs/',                    views.request_docs,      name='request_docs'),
    # Document submission (job seeker)
    path('<int:attempt_pk>/submit-docs/<str:step>/',  views.submit_docs,       name='submit_docs'),
    path('<int:attempt_pk>/docs-complete/',           views.docs_complete,     name='docs_complete'),
    # Document viewer (recruiter)
    path('<int:attempt_pk>/recruiter-docs/',          views.recruiter_docs,    name='recruiter_docs'),
    path('doc/<int:doc_pk>/download/',               views.download_doc,      name='download_doc'),
]
