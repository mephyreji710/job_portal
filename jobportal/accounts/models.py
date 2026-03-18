from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = 'admin'
    RECRUITER = 'recruiter'
    JOB_SEEKER = 'job_seeker'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (RECRUITER, 'Recruiter'),
        (JOB_SEEKER, 'Job Seeker'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=JOB_SEEKER)
    phone = models.CharField(max_length=20, blank=True)

    def is_admin_user(self):
        return self.role == self.ADMIN or self.is_superuser

    def is_recruiter_user(self):
        return self.role == self.RECRUITER

    def is_job_seeker_user(self):
        return self.role == self.JOB_SEEKER

    def get_dashboard_url(self):
        from django.urls import reverse
        if self.is_admin_user():
            return reverse('accounts:admin_dashboard')
        elif self.is_recruiter_user():
            return reverse('accounts:recruiter_dashboard')
        else:
            return reverse('accounts:jobseeker_dashboard')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class RecruiterProfile(models.Model):
    INDUSTRY_CHOICES = [
        ('technology',      'Technology & Software'),
        ('finance',         'Finance & Banking'),
        ('healthcare',      'Healthcare & Medical'),
        ('education',       'Education & Training'),
        ('manufacturing',   'Manufacturing'),
        ('retail',          'Retail & E-commerce'),
        ('consulting',      'Consulting & Professional Services'),
        ('media',           'Media & Entertainment'),
        ('real_estate',     'Real Estate & Construction'),
        ('logistics',       'Logistics & Supply Chain'),
        ('energy',          'Energy & Utilities'),
        ('government',      'Government & Public Sector'),
        ('nonprofit',       'Non-profit & NGO'),
        ('hospitality',     'Hospitality & Tourism'),
        ('other',           'Other'),
    ]
    SIZE_CHOICES = [
        ('1-10',       '1–10 employees'),
        ('11-50',      '11–50 employees'),
        ('51-200',     '51–200 employees'),
        ('201-500',    '201–500 employees'),
        ('501-1000',   '501–1,000 employees'),
        ('1001-5000',  '1,001–5,000 employees'),
        ('5000+',      '5,000+ employees'),
    ]
    TYPE_CHOICES = [
        ('private',    'Private Company'),
        ('public',     'Public Company'),
        ('startup',    'Startup'),
        ('nonprofit',  'Non-profit'),
        ('government', 'Government'),
        ('freelance',  'Freelance / Agency'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')

    # Basic info (from registration)
    company_name = models.CharField(max_length=200)
    company_website = models.URLField(blank=True)
    company_description = models.TextField(blank=True)

    # Extended company profile
    tagline         = models.CharField(max_length=200, blank=True)
    logo            = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    industry        = models.CharField(max_length=30, choices=INDUSTRY_CHOICES, blank=True)
    company_size    = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True)
    company_type    = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True)
    location        = models.CharField(max_length=150, blank=True)
    founded_year    = models.PositiveSmallIntegerField(null=True, blank=True)

    # Social / contact
    linkedin_url    = models.URLField(blank=True)
    twitter_url     = models.URLField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.company_name}"

    def get_completeness(self):
        fields = [
            self.company_name, self.tagline, self.company_description,
            self.industry, self.company_size, self.company_type,
            self.location, self.company_website,
            bool(self.logo), bool(self.founded_year),
        ]
        filled = sum(1 for f in fields if f)
        return int(filled / len(fields) * 100)


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jobseeker_profile')
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")
    experience_years = models.PositiveIntegerField(default=0)
    education = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
