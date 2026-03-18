from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display  = ('application', 'feedback_type', 'from_user', 'rating', 'is_anonymous', 'created_at')
    list_filter   = ('feedback_type', 'rating', 'is_anonymous')
    search_fields = ('from_user__email', 'comment', 'application__job__title')
    readonly_fields = ('created_at',)
