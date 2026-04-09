from django.db import models
from applications.models import Application


class Interview(models.Model):
    # Status
    STATUS_SCHEDULED = 'scheduled'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    # Type
    TYPE_VIDEO  = 'video'
    TYPE_PHONE  = 'phone'
    TYPE_ONSITE = 'onsite'
    TYPE_CHOICES = [
        ('video',  'Video Call'),
        ('phone',  'Phone Call'),
        ('onsite', 'On-site'),
    ]

    application    = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name='interview')

    scheduled_at   = models.DateTimeField()
    duration_mins  = models.PositiveSmallIntegerField(
        default=60, help_text='Duration in minutes')
    interview_type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default='video')
    location       = models.CharField(
        max_length=300, blank=True,
        help_text='Physical address (for on-site) or platform name (for video/phone)')
    meeting_link   = models.URLField(
        blank=True, help_text='Zoom / Google Meet / Teams link')
    notes          = models.TextField(
        blank=True,
        help_text='Message to the candidate — preparation tips, what to bring, etc.')
    status         = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='scheduled')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self):
        return (f"Interview: {self.application.applicant.email} for "
                f"{self.application.job.title} @ {self.scheduled_at:%Y-%m-%d %H:%M}")

    def status_color(self):
        return {
            'scheduled': '#3b82f6',
            'confirmed': '#10b981',
            'cancelled': '#ef4444',
            'completed': '#8b5cf6',
        }.get(self.status, '#6b7280')

    def status_bg(self):
        return {
            'scheduled': '#dbeafe',
            'confirmed': '#d1fae5',
            'cancelled': '#fee2e2',
            'completed': '#ede9fe',
        }.get(self.status, 'var(--gray-100)')

    def type_icon(self):
        return {'video': '📹', 'phone': '📞', 'onsite': '🏢'}.get(
            self.interview_type, '📅')
