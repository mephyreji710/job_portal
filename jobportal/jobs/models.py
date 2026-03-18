from django.db import models
from django.conf import settings
from django.utils import timezone
from accounts.models import RecruiterProfile


class JobPost(models.Model):
    STATUS_DRAFT  = 'draft'
    STATUS_ACTIVE = 'active'
    STATUS_PAUSED = 'paused'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_DRAFT,  'Draft'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_PAUSED, 'Paused'),
        (STATUS_CLOSED, 'Closed'),
    ]

    JOB_TYPE_CHOICES = [
        ('full_time',  'Full-time'),
        ('part_time',  'Part-time'),
        ('contract',   'Contract'),
        ('freelance',  'Freelance'),
        ('internship', 'Internship'),
    ]

    EXPERIENCE_CHOICES = [
        ('any',    'Any experience level'),
        ('entry',  'Entry Level (0–2 years)'),
        ('mid',    'Mid Level (2–5 years)'),
        ('senior', 'Senior Level (5–10 years)'),
        ('lead',   'Lead / Principal (10+ years)'),
    ]

    EDUCATION_CHOICES = [
        ('any',         'Any'),
        ('high_school', 'High School Diploma'),
        ('diploma',     'Diploma / Certificate'),
        ('bachelor',    "Bachelor's Degree"),
        ('master',      "Master's Degree"),
        ('phd',         'Ph.D / Doctorate'),
    ]

    SALARY_PERIOD_CHOICES = [
        ('monthly', 'Per Month'),
        ('yearly',  'Per Year'),
    ]

    # Relations
    recruiter = models.ForeignKey(
        RecruiterProfile, on_delete=models.CASCADE, related_name='jobs')

    # Core
    title       = models.CharField(max_length=200)
    job_type    = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    location    = models.CharField(max_length=200, blank=True)
    is_remote   = models.BooleanField(default=False)

    # Requirements
    required_skills       = models.TextField(blank=True, help_text='Comma-separated list of required skills')
    experience_level      = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES, default='any')
    experience_years_min  = models.PositiveSmallIntegerField(default=0)
    experience_years_max  = models.PositiveSmallIntegerField(null=True, blank=True)
    education_required    = models.CharField(max_length=20, choices=EDUCATION_CHOICES, default='any')

    # Content
    description      = models.TextField()
    responsibilities = models.TextField(blank=True)
    requirements     = models.TextField(blank=True)

    # Salary
    salary_min        = models.PositiveIntegerField(null=True, blank=True)
    salary_max        = models.PositiveIntegerField(null=True, blank=True)
    salary_currency   = models.CharField(max_length=3, default='USD')
    salary_period     = models.CharField(max_length=10, choices=SALARY_PERIOD_CHOICES, default='yearly')
    is_salary_visible = models.BooleanField(default=True)

    # Publishing
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    deadline   = models.DateField(null=True, blank=True)

    # Tracking
    views_count = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} @ {self.recruiter.company_name}"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_skills_list(self):
        """Return list of skill strings from comma-separated field."""
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    def get_salary_display(self):
        """Human-readable salary range string."""
        if not self.is_salary_visible:
            return 'Confidential'
        if not self.salary_min and not self.salary_max:
            return None
        cur = self.salary_currency
        period = 'mo' if self.salary_period == 'monthly' else 'yr'
        if self.salary_min and self.salary_max:
            return f"{cur} {self.salary_min:,} – {self.salary_max:,} / {period}"
        if self.salary_min:
            return f"From {cur} {self.salary_min:,} / {period}"
        return f"Up to {cur} {self.salary_max:,} / {period}"

    def is_expired(self):
        return bool(self.deadline and self.deadline < timezone.now().date())

    def days_since_posted(self):
        delta = timezone.now().date() - self.created_at.date()
        if delta.days == 0:
            return 'Today'
        if delta.days == 1:
            return '1 day ago'
        if delta.days < 30:
            return f'{delta.days} days ago'
        if delta.days < 60:
            return '1 month ago'
        return f'{delta.days // 30} months ago'

    def is_active(self):
        return self.status == self.STATUS_ACTIVE and not self.is_expired()


class SavedJob(models.Model):
    user    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_jobs')
    job     = models.ForeignKey(
        JobPost, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.email} ★ {self.job.title}"
