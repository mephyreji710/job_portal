from django.contrib import admin
from .models import JobPost


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display  = ('title', 'recruiter', 'job_type', 'status', 'is_remote', 'created_at', 'views_count')
    list_filter   = ('status', 'job_type', 'experience_level', 'is_remote')
    search_fields = ('title', 'recruiter__company_name', 'required_skills')
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    fieldsets = (
        ('Core',         {'fields': ('recruiter', 'title', 'job_type', 'status', 'deadline')}),
        ('Location',     {'fields': ('location', 'is_remote')}),
        ('Requirements', {'fields': ('required_skills', 'experience_level', 'experience_years_min', 'experience_years_max', 'education_required')}),
        ('Content',      {'fields': ('description', 'responsibilities', 'requirements')}),
        ('Salary',       {'fields': ('salary_min', 'salary_max', 'salary_currency', 'salary_period', 'is_salary_visible')}),
        ('Tracking',     {'fields': ('views_count', 'created_at', 'updated_at')}),
    )
