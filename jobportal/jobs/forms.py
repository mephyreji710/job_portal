from django import forms
from .models import JobPost


class JobPostForm(forms.ModelForm):
    class Meta:
        model  = JobPost
        fields = [
            'title', 'job_type', 'location', 'is_remote',
            'required_skills',
            'experience_level', 'experience_years_min', 'experience_years_max',
            'education_required',
            'description', 'responsibilities', 'requirements',
            'salary_min', 'salary_max', 'salary_currency', 'salary_period', 'is_salary_visible',
            'status', 'deadline',
        ]
        widgets = {
            'title':               forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Python Developer'}),
            'job_type':            forms.Select(attrs={'class': 'form-control'}),
            'location':            forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. New York, NY'}),
            'is_remote':           forms.CheckboxInput(attrs={'class': 'checkbox-input'}),
            'required_skills':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, Django, PostgreSQL, REST API'}),
            'experience_level':    forms.Select(attrs={'class': 'form-control'}),
            'experience_years_min':forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 40}),
            'experience_years_max':forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 40}),
            'education_required':  forms.Select(attrs={'class': 'form-control'}),
            'description':         forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Describe the role, team, and company culture…'}),
            'responsibilities':    forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': '• Lead backend development\n• Mentor junior developers\n…'}),
            'requirements':        forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': '• 3+ years of Django experience\n• Strong understanding of REST APIs\n…'}),
            'salary_min':          forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 60000'}),
            'salary_max':          forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 90000'}),
            'salary_currency':     forms.TextInput(attrs={'class': 'form-control', 'maxlength': 3, 'placeholder': 'USD'}),
            'salary_period':       forms.Select(attrs={'class': 'form-control'}),
            'is_salary_visible':   forms.CheckboxInput(attrs={'class': 'checkbox-input'}),
            'status':              forms.Select(attrs={'class': 'form-control'}),
            'deadline':            forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'title':               'Job Title',
            'job_type':            'Job Type',
            'location':            'Location',
            'is_remote':           'Remote / Work from home',
            'required_skills':     'Required Skills',
            'experience_level':    'Experience Level',
            'experience_years_min':'Min. Years of Experience',
            'experience_years_max':'Max. Years of Experience',
            'education_required':  'Minimum Education',
            'description':         'Job Description',
            'responsibilities':    'Responsibilities',
            'requirements':        'Requirements',
            'salary_min':          'Minimum Salary',
            'salary_max':          'Maximum Salary',
            'salary_currency':     'Currency',
            'salary_period':       'Pay Period',
            'is_salary_visible':   'Show salary to applicants',
            'status':              'Publication Status',
            'deadline':            'Application Deadline',
        }

    def clean(self):
        cleaned = super().clean()
        s_min = cleaned.get('salary_min')
        s_max = cleaned.get('salary_max')
        if s_min and s_max and s_min > s_max:
            self.add_error('salary_max', 'Maximum salary must be greater than minimum salary.')
        exp_min = cleaned.get('experience_years_min', 0)
        exp_max = cleaned.get('experience_years_max')
        if exp_max is not None and exp_min > exp_max:
            self.add_error('experience_years_max', 'Max experience must be ≥ minimum.')
        return cleaned
