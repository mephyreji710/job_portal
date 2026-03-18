from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Login / Logout
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Registration
    path('register/', views.register_role_select, name='register'),
    path('register/job-seeker/', views.register_jobseeker, name='register_jobseeker'),
    path('register/recruiter/', views.register_recruiter, name='register_recruiter'),

    # Email Verification
    path('registration-pending/', views.registration_pending, name='registration_pending'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),

    # Password Reset
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete, name='password_reset_complete'),

    # Dashboards
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/<int:pk>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('dashboard/recruiter/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('dashboard/job-seeker/', views.jobseeker_dashboard, name='jobseeker_dashboard'),
]
