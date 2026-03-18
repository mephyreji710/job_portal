import os
from django import forms

MAX_UPLOAD_MB = 10
ALLOWED_EXTENSIONS = ('.pdf', '.docx')


class ResumeUploadForm(forms.Form):
    file = forms.FileField(
        label='Resume File',
        help_text=f'PDF or DOCX only. Maximum {MAX_UPLOAD_MB} MB.',
    )

    def clean_file(self):
        f = self.cleaned_data['file']
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                'Unsupported file type. Only PDF (.pdf) and Word (.docx) files are accepted.'
            )
        if f.size > MAX_UPLOAD_MB * 1024 * 1024:
            raise forms.ValidationError(
                f'File too large. Maximum allowed size is {MAX_UPLOAD_MB} MB '
                f'(yours is {f.size / (1024*1024):.1f} MB).'
            )
        return f
