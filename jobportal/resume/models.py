from django.db import models
from django.conf import settings


def resume_upload_path(instance, filename):
    return f"resumes/user_{instance.user.pk}/{filename}"


class Resume(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PARSED  = 'parsed'
    STATUS_FAILED  = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PARSED,  'Parsed'),
        (STATUS_FAILED,  'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resumes',
    )
    file = models.FileField(upload_to=resume_upload_path)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)   # 'pdf' | 'docx'
    file_size = models.PositiveIntegerField()      # bytes

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    parse_error = models.TextField(blank=True)
    raw_text = models.TextField(blank=True)

    is_primary = models.BooleanField(default=False)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def get_file_size_display(self):
        if self.file_size < 1024:
            return f"{self.file_size} B"
        if self.file_size < 1024 * 1024:
            return f"{self.file_size // 1024} KB"
        return f"{self.file_size / (1024 * 1024):.1f} MB"

    def word_count(self):
        return len(self.raw_text.split()) if self.raw_text else 0

    def __str__(self):
        return f"{self.original_filename} ({self.user.email})"


class ParsedResume(models.Model):
    EDUCATION_LEVELS = [
        ('phd',         'Ph.D / Doctorate'),
        ('master',      "Master's Degree"),
        ('bachelor',    "Bachelor's Degree"),
        ('associate',   'Associate Degree'),
        ('diploma',     'Diploma / Certificate'),
        ('high_school', 'High School'),
        ('',            'Not detected'),
    ]

    resume = models.OneToOneField(
        Resume, on_delete=models.CASCADE, related_name='parsed')

    # Extracted contact info
    extracted_name    = models.CharField(max_length=150, blank=True)
    extracted_email   = models.EmailField(blank=True)
    extracted_phone   = models.CharField(max_length=40, blank=True)
    extracted_linkedin = models.URLField(blank=True)
    extracted_github   = models.URLField(blank=True)
    extracted_website  = models.URLField(blank=True)

    # Raw section texts
    summary_text        = models.TextField(blank=True)
    skills_text         = models.TextField(blank=True)
    education_text      = models.TextField(blank=True)
    experience_text     = models.TextField(blank=True)
    certifications_text = models.TextField(blank=True)
    projects_text       = models.TextField(blank=True)

    # Structured results
    extracted_skills = models.JSONField(default=list)
    # [{name, category}]
    extracted_keywords = models.JSONField(default=list)
    # [{word, count}]  top-20

    estimated_experience_years = models.FloatField(null=True, blank=True)
    education_level = models.CharField(
        max_length=20, blank=True, choices=EDUCATION_LEVELS)
    total_words     = models.PositiveIntegerField(default=0)
    total_keywords  = models.PositiveIntegerField(default=0)
    tech_skill_count = models.PositiveIntegerField(default=0)
    soft_skill_count = models.PositiveIntegerField(default=0)

    parsed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Parsed: {self.resume.original_filename}"


class ExtractedKeyword(models.Model):
    CATEGORY_CHOICES = [
        ('tech',  'Technical'),
        ('soft',  'Soft Skill'),
        ('other', 'Other'),
    ]

    parsed_resume = models.ForeignKey(
        ParsedResume, on_delete=models.CASCADE, related_name='keywords')
    word      = models.CharField(max_length=120)
    frequency = models.PositiveIntegerField(default=1)
    is_skill  = models.BooleanField(default=False)
    category  = models.CharField(
        max_length=10, choices=CATEGORY_CHOICES, default='other')

    class Meta:
        ordering = ['-frequency']
        unique_together = ('parsed_resume', 'word')

    def __str__(self):
        return f"{self.word} ({self.frequency}×)"


# ---------------------------------------------------------------------------
# Resume Builder
# ---------------------------------------------------------------------------

class BuiltResume(models.Model):
    TEMPLATE_CLASSIC = 'classic'
    TEMPLATE_MODERN  = 'modern'
    TEMPLATE_SIDEBAR = 'sidebar'
    TEMPLATE_CHOICES = [
        (TEMPLATE_CLASSIC, 'Classic Professional'),
        (TEMPLATE_MODERN,  'Modern Clean'),
        (TEMPLATE_SIDEBAR, 'Executive Sidebar'),
    ]

    user          = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='built_resumes')
    title         = models.CharField(max_length=200, help_text='e.g. "Software Developer Resume"')
    template_name = models.CharField(max_length=20, choices=TEMPLATE_CHOICES,
                                     default=TEMPLATE_CLASSIC)

    # Contact info — overrides profile if filled
    custom_name     = models.CharField(max_length=200, blank=True)
    custom_email    = models.EmailField(blank=True)
    custom_phone    = models.CharField(max_length=30, blank=True)
    custom_location = models.CharField(max_length=150, blank=True)
    custom_linkedin = models.URLField(blank=True)
    custom_website  = models.URLField(blank=True)

    # Resume-specific summary
    summary = models.TextField(blank=True,
                               help_text='A 3-5 sentence professional summary tailored for this resume.')

    # ── Customisation ──────────────────────────────────────────────────────
    FONT_SANS       = 'sans'
    FONT_INTER      = 'inter'
    FONT_SERIF      = 'serif'
    FONT_MONTSERRAT = 'montserrat'
    FONT_RALEWAY    = 'raleway'
    FONT_CHOICES = [
        (FONT_SANS,       'Modern Sans'),
        (FONT_INTER,      'Inter'),
        (FONT_SERIF,      'Classic Serif'),
        (FONT_MONTSERRAT, 'Montserrat'),
        (FONT_RALEWAY,    'Raleway'),
    ]

    accent_color  = models.CharField(max_length=7, blank=True, default='',
                                     help_text='Hex colour e.g. #4f46e5 — leave blank for template default')
    font_family   = models.CharField(max_length=20, choices=FONT_CHOICES, default=FONT_SANS)
    section_order = models.CharField(
        max_length=120, blank=True,
        default='summary,experience,skills,education,certs',
        help_text='Comma-separated section keys controlling display order')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} [{self.get_template_name_display()}]"
