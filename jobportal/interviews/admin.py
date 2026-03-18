from django.contrib import admin
from .models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display  = ('application', 'interview_type', 'scheduled_at',
                     'duration_mins', 'status', 'created_at')
    list_filter   = ('status', 'interview_type', 'scheduled_at')
    search_fields = ('application__applicant__email', 'application__job__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('scheduled_at',)
