from django.db import models
from django.conf import settings
from applications.models import Application


class Assessment(models.Model):
    """A 25-question MCQ assessment sent by a recruiter to a shortlisted candidate."""

    application = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name='assessment'
    )
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    time_limit_mins = models.PositiveIntegerField(
        default=30, help_text='0 = no limit'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_assessments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    doc_requested = models.BooleanField(
        default=False,
        help_text='Recruiter has requested document verification from this candidate'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.application.applicant.email}"

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def attempt_obj(self):
        """Return the attempt if it exists, else None."""
        try:
            return self.attempt
        except Exception:
            return None


class Question(models.Model):
    OPTION_CHOICES = [('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')]

    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name='questions'
    )
    order = models.PositiveIntegerField(default=0)
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=OPTION_CHOICES)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:60]}"

    def get_option_text(self, letter):
        return getattr(self, f'option_{letter}', '')


class AssessmentAttempt(models.Model):
    """Records a job seeker's attempt at an assessment."""

    assessment = models.OneToOneField(
        Assessment, on_delete=models.CASCADE, related_name='attempt'
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assessment_attempts'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)       # 0–100 percentage
    correct_count = models.PositiveIntegerField(default=0)
    total_count = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.applicant.email} — {self.score}%"

    @property
    def score_label(self):
        if self.score is None:
            return 'N/A'
        if self.score >= 80:
            return 'Excellent'
        elif self.score >= 60:
            return 'Good'
        elif self.score >= 40:
            return 'Fair'
        return 'Needs Improvement'

    @property
    def score_color(self):
        if self.score is None:
            return '#6b7280'
        if self.score >= 80:
            return '#10b981'
        elif self.score >= 60:
            return '#3b82f6'
        elif self.score >= 40:
            return '#f59e0b'
        return '#ef4444'

    @property
    def wrong_count(self):
        return self.total_count - self.correct_count

    @property
    def score_bg(self):
        if self.score is None:
            return '#f3f4f6'
        if self.score >= 80:
            return '#d1fae5'
        elif self.score >= 60:
            return '#dbeafe'
        elif self.score >= 40:
            return '#fef3c7'
        return '#fee2e2'


class DocumentSubmission(models.Model):
    """Documents uploaded by a job seeker after passing the assessment (score >= 20/25)."""

    TYPE_EXPERIENCE   = 'experience'
    TYPE_CERTIFICATE  = 'certificate'
    TYPE_CRIMINAL     = 'criminal'

    TYPE_CHOICES = [
        (TYPE_EXPERIENCE,  'Work Experience'),
        (TYPE_CERTIFICATE, 'Certificate'),
        (TYPE_CRIMINAL,    'Criminal Record'),
    ]

    attempt       = models.ForeignKey(
        AssessmentAttempt, on_delete=models.CASCADE, related_name='documents'
    )
    document_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title         = models.CharField(max_length=200, blank=True)
    file          = models.FileField(upload_to='submission_docs/%Y/%m/')
    notes         = models.TextField(blank=True)
    submitted_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['document_type', 'submitted_at']

    def __str__(self):
        return f"{self.get_document_type_display()} — {self.attempt.applicant.email}"

    @property
    def filename(self):
        import os
        return os.path.basename(self.file.name)


class Answer(models.Model):
    """Stores a single answer given by an applicant for a question."""
    OPTION_CHOICES = [('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')]

    attempt = models.ForeignKey(
        AssessmentAttempt, on_delete=models.CASCADE, related_name='answers'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers'
    )
    selected_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('attempt', 'question')
        ordering = ['question__order']

    def __str__(self):
        mark = '✓' if self.is_correct else '✗'
        return f"Q{self.question.order}: {self.selected_option.upper()} ({mark})"
