from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Feedback(models.Model):
    TYPE_C2CO = 'candidate_to_company'
    TYPE_CO2C = 'company_to_candidate'

    TYPE_CHOICES = [
        (TYPE_C2CO, 'Candidate to Company'),
        (TYPE_CO2C, 'Company to Candidate'),
    ]

    application   = models.ForeignKey(
        'applications.Application', on_delete=models.CASCADE, related_name='feedbacks')
    from_user     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback_given')
    feedback_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    rating        = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment       = models.TextField(blank=True)
    is_anonymous  = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('application', 'feedback_type')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_feedback_type_display()} | {self.rating} stars"

    @property
    def stars_filled(self):
        return range(self.rating)

    @property
    def stars_empty(self):
        return range(5 - self.rating)

    @property
    def star_display(self):
        return '★' * self.rating + '☆' * (5 - self.rating)
