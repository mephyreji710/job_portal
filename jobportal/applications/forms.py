from django import forms
from .models import Application


class ApplyForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'full_name', 'phone', 'applicant_location',
            'skills_summary', 'experience_summary',
            'cover_letter', 'resume_file',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 000-0000',
            }),
            'applicant_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country',
            }),
            'skills_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g. Python, Django, SQL, REST APIs, React...',
            }),
            'experience_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': (
                    'Briefly describe your work experience relevant to this role.\n'
                    'e.g. 3 years as a backend developer at XYZ Corp building REST APIs...'
                ),
            }),
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': (
                    'Optional: Introduce yourself, explain why you are a great fit, '
                    'or highlight any relevant achievements...'
                ),
            }),
            'resume_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
            }),
        }
        labels = {
            'full_name':           'Full Name',
            'phone':               'Phone Number',
            'applicant_location':  'Location',
            'skills_summary':      'Key Skills',
            'experience_summary':  'Work Experience',
            'cover_letter':        'Cover Letter',
            'resume_file':         'Upload Resume',
        }
