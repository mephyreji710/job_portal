from django.db import models
from django.conf import settings
from jobs.models import JobPost


class MatchScore(models.Model):
    job = models.ForeignKey(
        JobPost, on_delete=models.CASCADE, related_name='match_scores')
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_scores')

    # Component scores (0–100)
    skills_score     = models.FloatField(default=0)
    experience_score = models.FloatField(default=0)
    education_score  = models.FloatField(default=0)
    keywords_score   = models.FloatField(default=0)
    total_score      = models.FloatField(default=0)

    # Detailed breakdown
    matched_skills   = models.JSONField(default=list)   # [str, ...]
    missing_skills   = models.JSONField(default=list)   # [str, ...]
    matched_keywords = models.JSONField(default=list)   # [str, ...]

    experience_years_found = models.FloatField(default=0)
    education_rank_found   = models.PositiveSmallIntegerField(default=0)

    # Recruiter decision
    STATUS_NEW         = 'new'
    STATUS_REVIEWED    = 'reviewed'
    STATUS_SHORTLISTED = 'shortlisted'
    STATUS_REJECTED    = 'rejected'
    STATUS_CHOICES = [
        ('new',         'New'),
        ('reviewed',    'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected',    'Rejected'),
    ]
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    recruiter_notes = models.TextField(blank=True)

    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'candidate')
        ordering = ['-total_score']

    def __str__(self):
        return f"{self.candidate.email} × {self.job.title} = {self.total_score:.1f}%"

    def score_label(self):
        if self.total_score >= 80:
            return 'Excellent'
        if self.total_score >= 60:
            return 'Good'
        if self.total_score >= 40:
            return 'Fair'
        return 'Low'

    def score_color(self):
        if self.total_score >= 80:
            return '#10b981'
        if self.total_score >= 60:
            return '#3b82f6'
        if self.total_score >= 40:
            return '#f59e0b'
        return '#ef4444'
