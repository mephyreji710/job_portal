import datetime
from django import forms
from accounts.models import RecruiterProfile
from .models import HRMember


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = [
            'company_name', 'tagline', 'logo',
            'industry', 'company_size', 'company_type',
            'location', 'founded_year',
            'company_website', 'company_description',
            'linkedin_url', 'twitter_url',
        ]
        widgets = {
            'company_name':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Acme Corporation'}),
            'tagline':             forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Building the future of work'}),
            'logo':                forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'industry':            forms.Select(attrs={'class': 'form-control'}),
            'company_size':        forms.Select(attrs={'class': 'form-control'}),
            'company_type':        forms.Select(attrs={'class': 'form-control'}),
            'location':            forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. New York, NY'}),
            'founded_year':        forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2015', 'min': 1800, 'max': datetime.date.today().year}),
            'company_website':     forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourcompany.com'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your company, culture, and what makes it a great place to work…'}),
            'linkedin_url':        forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/company/yourcompany'}),
            'twitter_url':         forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://twitter.com/yourcompany'}),
        }
        labels = {
            'company_name':    'Company Name',
            'tagline':         'Tagline',
            'logo':            'Company Logo',
            'industry':        'Industry',
            'company_size':    'Company Size',
            'company_type':    'Company Type',
            'location':        'Headquarters Location',
            'founded_year':    'Founded Year',
            'company_website': 'Website',
            'company_description': 'About the Company',
            'linkedin_url':    'LinkedIn URL',
            'twitter_url':     'Twitter / X URL',
        }


class HRMemberForm(forms.ModelForm):
    class Meta:
        model = HRMember
        fields = ['name', 'email', 'phone', 'role']
        widgets = {
            'name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@company.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000 (optional)'}),
            'role':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. HR Manager, Talent Recruiter'}),
        }
