from django.contrib import admin
from .models import Assessment, Question, AssessmentAttempt, Answer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('order', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'selected_option', 'is_correct')
    can_delete = False


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'application', 'created_by', 'question_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'application__applicant__email')
    inlines = [QuestionInline]
    readonly_fields = ('created_at',)


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'applicant', 'score', 'correct_count', 'total_count', 'is_completed', 'completed_at')
    list_filter = ('is_completed',)
    search_fields = ('applicant__email',)
    readonly_fields = ('started_at', 'completed_at')
    inlines = [AnswerInline]
