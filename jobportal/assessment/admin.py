from django.contrib import admin
from .models import Assessment, Question, AssessmentAttempt, Answer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('order', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option')


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'job', 'recruiter', 'question_count', 'pass_mark', 'time_limit_minutes')
    inlines = [QuestionInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'selected_option', 'is_correct')


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('application', 'assessment', 'score', 'status', 'assigned_at', 'completed_at')
    list_filter = ('status',)
    inlines = [AnswerInline]
