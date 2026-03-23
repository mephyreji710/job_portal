from django.db import models
from accounts.models import RecruiterProfile


class HRMember(models.Model):
    company  = models.ForeignKey(RecruiterProfile, on_delete=models.CASCADE, related_name='hr_members')
    name     = models.CharField(max_length=150)
    email    = models.EmailField()
    phone    = models.CharField(max_length=30, blank=True)
    role     = models.CharField(max_length=100, default='HR Manager')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ('company', 'email')

    def __str__(self):
        return f"{self.name} — {self.role} ({self.company.company_name})"
