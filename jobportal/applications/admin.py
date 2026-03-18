from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display  = ('applicant', 'job', 'status', 'applied_at', 'updated_at')
    list_filter   = ('status', 'applied_at')
    search_fields = ('applicant__email', 'job__title', 'job__recruiter__company_name')
    readonly_fields = ('applied_at', 'updated_at')
    ordering = ('-applied_at',)
