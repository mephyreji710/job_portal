from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_APP_RECEIVED      = 'app_received'
    TYPE_SHORTLISTED       = 'shortlisted'
    TYPE_REJECTED          = 'rejected'
    TYPE_HIRED             = 'hired'
    TYPE_INTERVIEW         = 'interview'
    TYPE_INTERVIEW_CONFIRM = 'interview_confirmed'
    TYPE_INTERVIEW_CANCEL  = 'interview_cancelled'

    TYPE_CHOICES = [
        (TYPE_APP_RECEIVED,      'Application Received'),
        (TYPE_SHORTLISTED,       'Shortlisted'),
        (TYPE_REJECTED,          'Application Rejected'),
        (TYPE_HIRED,             'Hired'),
        (TYPE_INTERVIEW,         'Interview Scheduled'),
        (TYPE_INTERVIEW_CONFIRM, 'Interview Confirmed'),
        (TYPE_INTERVIEW_CANCEL,  'Interview Cancelled'),
    ]

    ICON = {
        TYPE_APP_RECEIVED:      '&#128232;',
        TYPE_SHORTLISTED:       '&#11088;',
        TYPE_REJECTED:          '&#10005;',
        TYPE_HIRED:             '&#127881;',
        TYPE_INTERVIEW:         '&#128197;',
        TYPE_INTERVIEW_CONFIRM: '&#10003;',
        TYPE_INTERVIEW_CANCEL:  '&#10005;',
    }

    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name='notifications')
    from_user   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='notifications_sent')
    notif_type  = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title       = models.CharField(max_length=200)
    message     = models.TextField(blank=True)
    link        = models.CharField(max_length=500, blank=True)
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notif_type}] {self.title} → {self.user}"

    @property
    def icon(self):
        return self.ICON.get(self.notif_type, '&#128276;')

    @property
    def color(self):
        mapping = {
            self.TYPE_APP_RECEIVED:      'var(--indigo)',
            self.TYPE_SHORTLISTED:       '#d97706',
            self.TYPE_REJECTED:          '#dc2626',
            self.TYPE_HIRED:             'var(--green)',
            self.TYPE_INTERVIEW:         'var(--indigo)',
            self.TYPE_INTERVIEW_CONFIRM: 'var(--green)',
            self.TYPE_INTERVIEW_CANCEL:  '#dc2626',
        }
        return mapping.get(self.notif_type, 'var(--blue)')

    @property
    def bg(self):
        mapping = {
            self.TYPE_APP_RECEIVED:      '#eef2ff',
            self.TYPE_SHORTLISTED:       '#fffbeb',
            self.TYPE_REJECTED:          '#fef2f2',
            self.TYPE_HIRED:             '#f0fdf4',
            self.TYPE_INTERVIEW:         '#eef2ff',
            self.TYPE_INTERVIEW_CONFIRM: '#f0fdf4',
            self.TYPE_INTERVIEW_CANCEL:  '#fef2f2',
        }
        return mapping.get(self.notif_type, '#f8fafc')
