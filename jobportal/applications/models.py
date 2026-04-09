from django.db import models
from django.conf import settings
from jobs.models import JobPost


class Application(models.Model):
    STATUS_PENDING     = 'pending'
    STATUS_REVIEWED    = 'reviewed'
    STATUS_SHORTLISTED = 'shortlisted'
    STATUS_REJECTED    = 'rejected'
    STATUS_HIRED       = 'hired'
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('reviewed',    'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected',    'Rejected'),
        ('hired',       'Hired'),
    ]

    job      = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')

    resume = models.ForeignKey(
        'resume.Resume',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='applications',
    )
    # Application form fields filled by job seeker at apply time
    full_name            = models.CharField(max_length=200, blank=True)
    phone                = models.CharField(max_length=30, blank=True)
    applicant_location   = models.CharField(max_length=200, blank=True)
    skills_summary       = models.TextField(blank=True, help_text='Comma-separated skills')
    experience_summary   = models.TextField(blank=True, help_text='Brief work experience summary')
    resume_file          = models.FileField(upload_to='application_resumes/', blank=True, null=True)

    cover_letter    = models.TextField(blank=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    recruiter_notes = models.TextField(blank=True)

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.email} → {self.job.title} [{self.get_status_display()}]"

    def status_color(self):
        return {
            'pending':     '#6b7280',
            'reviewed':    '#3b82f6',
            'shortlisted': '#10b981',
            'rejected':    '#ef4444',
            'hired':       '#8b5cf6',
        }.get(self.status, '#6b7280')

    def get_skills_list(self):
        """Return skills as a list of stripped strings."""
        if not self.skills_summary:
            return []
        return [s.strip() for s in self.skills_summary.split(',') if s.strip()]

    @property
    def assessment_obj(self):
        """Return the linked Assessment if one exists, otherwise None."""
        try:
            return self.assessment
        except Exception:
            return None

    def status_bg(self):
        return {
            'pending':     'var(--gray-100)',
            'reviewed':    '#dbeafe',
            'shortlisted': '#d1fae5',
            'rejected':    '#fee2e2',
            'hired':       '#ede9fe',
        }.get(self.status, 'var(--gray-100)')
