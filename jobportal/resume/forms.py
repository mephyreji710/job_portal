import os
from django import forms
from .models import BuiltResume

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


class BuiltResumeForm(forms.ModelForm):
    class Meta:
        model  = BuiltResume
        fields = [
            'title', 'template_name', 'summary',
            'personal_details',
            'custom_name', 'custom_email', 'custom_phone',
            'custom_location', 'custom_linkedin', 'custom_website',
            'accent_color', 'font_family', 'section_order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'fc', 'placeholder': 'e.g. Software Developer Resume — Google 2025',
            }),
            'template_name': forms.RadioSelect(),
            'summary': forms.Textarea(attrs={
                'class': 'fc', 'rows': 5,
                'placeholder': (
                    'Write a 3-5 sentence professional summary highlighting your '
                    'key strengths, years of experience, and career goals...'
                ),
            }),
            'custom_name':     forms.TextInput(attrs={'class': 'fc', 'placeholder': 'Full name (leave blank to use profile name)'}),
            'custom_email':    forms.EmailInput(attrs={'class': 'fc', 'placeholder': 'email@example.com'}),
            'custom_phone':    forms.TextInput(attrs={'class': 'fc', 'placeholder': '+1 (555) 000-0000'}),
            'custom_location': forms.TextInput(attrs={'class': 'fc', 'placeholder': 'City, State, Country'}),
            'custom_linkedin': forms.URLInput(attrs={'class': 'fc', 'placeholder': 'linkedin.com/in/yourprofile'}),
            'custom_website':  forms.URLInput(attrs={'class': 'fc', 'placeholder': 'yourportfolio.com'}),
            'personal_details': forms.Textarea(attrs={
                'class': 'fc', 'rows': 3,
                'placeholder': (
                    'e.g. GitHub: github.com/you  |  Languages: English (Native), Spanish (B2)  '
                    '|  Driving licence: Full  |  References available on request'
                ),
            }),
            'accent_color':    forms.TextInput(attrs={'type': 'color', 'class': 'color-input'}),
            'font_family':     forms.RadioSelect(),
            'section_order':   forms.HiddenInput(),
        }
        labels = {
            'title':          'Resume Title',
            'template_name':  'Choose Template',
            'summary':        'Professional Summary',
            'custom_name':    'Full Name',
            'custom_email':   'Email',
            'custom_phone':   'Phone',
            'custom_location':'Location',
            'custom_linkedin':'LinkedIn URL',
            'custom_website': 'Website / Portfolio',
            'accent_color':   'Accent Colour',
            'font_family':    'Font Style',
            'personal_details': 'Additional Information (Optional)',
            'section_order':  'Section Order',
        }
