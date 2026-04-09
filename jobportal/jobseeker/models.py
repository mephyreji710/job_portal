






from django.db import models
from django.conf import settings


class JobSeekerProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not', 'Prefer not to say'),
    ]
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
        ('any', 'Any'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='js_profile',
    )

    # Personal Details
    headline = models.CharField(max_length=120, blank=True,
                                help_text='e.g. "Senior Python Developer"')
    bio = models.TextField(max_length=1200, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    location = models.CharField(max_length=100, blank=True,
                                help_text='City, Country')
    address = models.TextField(blank=True,
                               help_text='Street address, city, state, postal code, country')
    nationality = models.CharField(max_length=60, blank=True)
    languages = models.CharField(max_length=300, blank=True,
                                 help_text='Comma-separated languages, e.g. English, Hindi, French')

    # Online Presence
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    # Profile Picture
    profile_picture = models.ImageField(
        upload_to='profile_pics/', blank=True, null=True)

    # Job Preferences
    is_available = models.BooleanField(default=True)
    preferred_job_type = models.CharField(
        max_length=20, choices=JOB_TYPE_CHOICES, blank=True, default='any')
    expected_salary = models.PositiveIntegerField(
        null=True, blank=True, help_text='Monthly salary in USD')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ---------------------------------------------------------------------------
    # Completeness
    # ---------------------------------------------------------------------------

    COMPLETENESS_CHECKS = [
        ('profile_picture', 'Profile picture'),
        ('headline',        'Professional headline'),
        ('bio',             'About / Bio'),
        ('location',        'Location'),
        ('phone',           'Phone number'),
        ('skills',          'Skills (at least 1)'),
        ('education',       'Education (at least 1)'),
        ('experience',      'Work experience (at least 1)'),
        ('certifications',  'Certifications (at least 1)'),
        ('online',          'LinkedIn or Website'),
    ]

    def _check(self, key):
        if key == 'phone':
            return bool(self.user.phone)
        if key == 'skills':
            return self.skills.exists()
        if key == 'education':
            return self.education.exists()
        if key == 'experience':
            return self.experience.exists()
        if key == 'certifications':
            return self.certifications.exists()
        if key == 'online':
            return bool(self.linkedin_url or self.website)
        return bool(getattr(self, key, None))

    def get_completeness(self):
        score = sum(self._check(k) for k, _ in self.COMPLETENESS_CHECKS)
        return int(score / len(self.COMPLETENESS_CHECKS) * 100)

    def get_missing_items(self):
        return [label for key, label in self.COMPLETENESS_CHECKS
                if not self._check(key)]

    def get_completeness_color(self):
        pct = self.get_completeness()
        if pct < 40:
            return '#ef4444'
        if pct < 70:
            return '#f59e0b'
        return '#10b981'

    def get_languages_list(self):
        """Return list of language strings from the comma-separated field."""
        return [l.strip() for l in self.languages.split(',') if l.strip()]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} — Profile"


class Skill(models.Model):
    PROFICIENCY_CHOICES = [
        ('beginner',     'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced',     'Advanced'),
        ('expert',       'Expert'),
    ]
    PROFICIENCY_PCT = {
        'beginner': 25, 'intermediate': 50, 'advanced': 75, 'expert': 100,
    }

    profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=80)
    proficiency = models.CharField(
        max_length=20, choices=PROFICIENCY_CHOICES, default='intermediate')
    years_of_experience = models.PositiveSmallIntegerField(
        default=0, help_text='Years using this skill')

    class Meta:
        ordering = ['name']
        unique_together = ('profile', 'name')

    def get_pct(self):
        return self.PROFICIENCY_PCT.get(self.proficiency, 50)

    def __str__(self):
        return f"{self.name} ({self.get_proficiency_display()})"


class Education(models.Model):
    DEGREE_CHOICES = [
        ('high_school', 'High School Diploma'),
        ('associate',   'Associate Degree'),
        ('bachelor',    "Bachelor's Degree"),
        ('master',      "Master's Degree"),
        ('phd',         'Ph.D / Doctorate'),
        ('certificate', 'Certificate / Diploma'),
        ('other',       'Other'),
    ]

    profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name='education')
    degree = models.CharField(max_length=30, choices=DEGREE_CHOICES)
    field_of_study = models.CharField(max_length=120)
    institution = models.CharField(max_length=200)
    start_year = models.PositiveSmallIntegerField()
    end_year = models.PositiveSmallIntegerField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    grade = models.CharField(max_length=50, blank=True,
                             help_text='GPA, percentage, grade, etc.')
    description = models.TextField(
        blank=True, help_text='Activities, achievements, thesis, etc.')

    class Meta:
        ordering = ['-start_year']

    def __str__(self):
        return (f"{self.get_degree_display()} in {self.field_of_study} "
                f"— {self.institution}")


class Experience(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time',  'Full-time'),
        ('part_time',  'Part-time'),
        ('contract',   'Contract'),
        ('freelance',  'Freelance'),
        ('internship', 'Internship'),
        ('volunteer',  'Volunteer'),
    ]

    profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name='experience')
    job_title = models.CharField(max_length=120)
    company = models.CharField(max_length=200)
    employment_type = models.CharField(
        max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(
        blank=True, help_text='Key responsibilities and achievements')

    class Meta:
        ordering = ['-start_date']

    def get_duration(self):
        from datetime import date
        end = date.today() if self.is_current else self.end_date
        if not end:
            return ''
        months = ((end.year - self.start_date.year) * 12
                  + end.month - self.start_date.month)
        years, rem = divmod(months, 12)
        if years and rem:
            return f"{years}y {rem}m"
        if years:
            return f"{years} yr{'s' if years > 1 else ''}"
        return f"{rem} mo"

    def __str__(self):
        return f"{self.job_title} at {self.company}"


class Certification(models.Model):
    profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    does_not_expire = models.BooleanField(default=False)
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True)

    class Meta:
        ordering = ['-issue_date']

    def is_expired(self):
        from datetime import date
        if self.does_not_expire or not self.expiry_date:
            return False
        return self.expiry_date < date.today()

    def __str__(self):
        return f"{self.name} — {self.issuing_organization}"
