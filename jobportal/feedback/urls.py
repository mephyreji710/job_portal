from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('applications/<int:application_pk>/give/', views.give_feedback,    name='give'),
    path('company/<int:profile_pk>/reviews/',       views.company_reviews,  name='company_reviews'),
    path('my-ratings/',                             views.my_ratings,       name='my_ratings'),
]
