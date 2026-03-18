from django.contrib import admin
from .models import MatchScore


@admin.register(MatchScore)
class MatchScoreAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'total_score', 'skills_score',
                    'experience_score', 'education_score', 'keywords_score', 'computed_at')
    list_filter  = ('computed_at',)
    search_fields = ('candidate__email', 'job__title')
    readonly_fields = ('computed_at',)
    ordering = ('-total_score',)
