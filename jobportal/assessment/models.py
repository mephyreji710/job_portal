from django.db import models
from django.conf import settings


class Assessment(models.Model):
    job = models.OneToOneField(
        'jobs.JobPost', on_delete=models.CASCADE, related_name='assessment'
    )
    recruiter = models.ForeignKey(
        'accounts.RecruiterProfile', on_delete=models.CASCADE, related_name='assessments'
    )
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    pass_mark = models.PositiveIntegerField(default=20)
    time_limit_minutes = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Assessment: {self.title} ({self.job.title})"

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def is_complete(self):
        return self.questions.count() == 25


class Question(models.Model):
    OPTION_CHOICES = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]

    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name='questions'
    )
    text = models.TextField()
    option_a = models.CharField(max_length=400)
    option_b = models.CharField(max_length=400)
    option_c = models.CharField(max_length=400)
    option_d = models.CharField(max_length=400)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'pk']

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"

    def get_option_text(self, letter):
        return {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d,
        }.get(letter, '')


class AssessmentAttempt(models.Model):
    STATUS_PENDING     = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_PASSED      = 'passed'
    STATUS_FAILED      = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING,     'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_PASSED,      'Passed'),
        (STATUS_FAILED,      'Failed'),
    ]

    application = models.OneToOneField(
        'applications.Application', on_delete=models.CASCADE,
        related_name='assessment_attempt'
    )
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name='attempts'
    )
    score = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    assigned_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Attempt by {self.application.applicant} — {self.assessment.title}"

    @property
    def total_questions(self):
        return self.assessment.questions.count()

    @property
    def passed(self):
        return self.score is not None and self.score >= self.assessment.pass_mark


class Answer(models.Model):
    attempt = models.ForeignKey(
        AssessmentAttempt, on_delete=models.CASCADE, related_name='answers'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers'
    )
    selected_option = models.CharField(max_length=1)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('attempt', 'question')
