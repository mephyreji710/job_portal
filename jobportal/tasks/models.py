from django.db import models
from applications.models import Application
from accounts.models import RecruiterProfile


class Task(models.Model):
    ATTACHMENT_NONE  = 'none'
    ATTACHMENT_FILE  = 'file'
    ATTACHMENT_VIDEO = 'video'
    ATTACHMENT_IMAGE = 'image'
    ATTACHMENT_LINK  = 'link'

    ATTACHMENT_CHOICES = [
        (ATTACHMENT_NONE,  'No Attachment'),
        (ATTACHMENT_FILE,  'File (PDF, DOC, DOCX, etc.)'),
        (ATTACHMENT_VIDEO, 'Video'),
        (ATTACHMENT_IMAGE, 'Image'),
        (ATTACHMENT_LINK,  'URL / Link'),
    ]

    STATUS_PENDING    = 'pending'
    STATUS_INPROGRESS = 'in_progress'
    STATUS_SUBMITTED  = 'submitted'
    STATUS_APPROVED   = 'approved'
    STATUS_REJECTED   = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING,    'Pending'),
        (STATUS_INPROGRESS, 'In Progress'),
        (STATUS_SUBMITTED,  'Submitted'),
        (STATUS_APPROVED,   'Approved'),
        (STATUS_REJECTED,   'Rejected'),
    ]

    application     = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='tasks')
    recruiter       = models.ForeignKey(RecruiterProfile, on_delete=models.CASCADE, related_name='assigned_tasks')
    title           = models.CharField(max_length=200)
    description     = models.TextField()
    attachment_type = models.CharField(max_length=10, choices=ATTACHMENT_CHOICES, default=ATTACHMENT_NONE)
    attachment      = models.FileField(upload_to='task_attachments/', blank=True, null=True)
    attachment_url  = models.URLField(blank=True)
    due_date        = models.DateField(blank=True, null=True)
    status          = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.application.applicant.get_full_name()}"

    @property
    def status_color(self):
        return {
            'pending':     '#d97706',
            'in_progress': '#2563eb',
            'submitted':   '#7c3aed',
            'approved':    '#059669',
            'rejected':    '#dc2626',
        }.get(self.status, '#6b7280')

    @property
    def status_bg(self):
        return {
            'pending':     '#fffbeb',
            'in_progress': '#eff6ff',
            'submitted':   '#f5f3ff',
            'approved':    '#ecfdf5',
            'rejected':    '#fef2f2',
        }.get(self.status, '#f9fafb')

    @property
    def status_label(self):
        labels = dict(self.STATUS_CHOICES)
        return labels.get(self.status, self.status)


class TaskSubmission(models.Model):
    task               = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='submission')
    submission_text    = models.TextField(blank=True)
    submission_file    = models.FileField(upload_to='task_submissions/', blank=True, null=True)
    submitted_at       = models.DateTimeField(auto_now_add=True)
    recruiter_feedback = models.TextField(blank=True)
    reviewed_at        = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Submission for: {self.task.title}"
