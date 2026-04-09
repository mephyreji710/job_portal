from datetime import date
from django import forms
from .models import JobSeekerProfile, Skill, Education, Experience, Certification

YEAR_CHOICES = [(y, y) for y in range(date.today().year, 1959, -1)]


class PersonalDetailsForm(forms.ModelForm):
    # Phone lives on User model, so we handle it manually
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'placeholder': '+1 (555) 000-0000'}),
    )
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'First name'}),
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Last name'}),
    )

    class Meta:
        model = JobSeekerProfile
        fields = [
            'profile_picture', 'headline', 'bio',
            'date_of_birth', 'gender', 'location', 'address', 'nationality',
            'languages',
            'website', 'linkedin_url', 'github_url',
            'is_available', 'preferred_job_type', 'expected_salary',
        ]
        widgets = {
            'headline':     forms.TextInput(attrs={'placeholder': 'e.g. Senior Python Developer'}),
            'bio':          forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell employers about yourself…'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'location':     forms.TextInput(attrs={'placeholder': 'City, Country'}),
            'address':      forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'e.g. 12 Main Street, Koramangala, Bangalore 560034, Karnataka, India',
            }),
            'nationality':  forms.TextInput(attrs={'placeholder': 'e.g. Indian'}),
            'languages':    forms.TextInput(attrs={
                'placeholder': 'e.g. English, Hindi, Tamil, French',
            }),
            'website':      forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/yourname'}),
            'github_url':   forms.URLInput(attrs={'placeholder': 'https://github.com/yourname'}),
            'expected_salary': forms.NumberInput(attrs={'placeholder': '5000'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user
        if user:
            self.fields['phone'].initial = user.phone
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self._user:
            self._user.phone = self.cleaned_data.get('phone', '')
            self._user.first_name = self.cleaned_data.get('first_name', '')
            self._user.last_name = self.cleaned_data.get('last_name', '')
            self._user.save(update_fields=['phone', 'first_name', 'last_name'])
        if commit:
            profile.save()
        return profile


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'proficiency', 'years_of_experience']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Python'}),
            'years_of_experience': forms.NumberInput(attrs={'min': 0, 'max': 50, 'placeholder': '0'}),
        }


class EducationForm(forms.ModelForm):
    start_year = forms.TypedChoiceField(
        choices=YEAR_CHOICES, coerce=int,
        widget=forms.Select(),
    )
    end_year = forms.TypedChoiceField(
        choices=[('', '— Present —')] + YEAR_CHOICES,
        coerce=lambda x: int(x) if x else None,
        required=False,
    )

    class Meta:
        model = Education
        fields = [
            'degree', 'field_of_study', 'institution',
            'start_year', 'end_year', 'is_current',
            'grade', 'description',
        ]
        widgets = {
            'field_of_study': forms.TextInput(attrs={'placeholder': 'e.g. Computer Science'}),
            'institution':    forms.TextInput(attrs={'placeholder': 'e.g. MIT'}),
            'grade':          forms.TextInput(attrs={'placeholder': 'e.g. 3.8 GPA, First Class'}),
            'description':    forms.Textarea(attrs={'rows': 3, 'placeholder': 'Activities, thesis, achievements…'}),
        }

    def clean(self):
        cleaned = super().clean()
        sy = cleaned.get('start_year')
        ey = cleaned.get('end_year')
        is_current = cleaned.get('is_current')
        if not is_current and ey and sy and ey < sy:
            self.add_error('end_year', 'End year cannot be before start year.')
        return cleaned


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            'job_title', 'company', 'employment_type', 'location',
            'start_date', 'end_date', 'is_current', 'description',
        ]
        widgets = {
            'job_title':   forms.TextInput(attrs={'placeholder': 'e.g. Backend Developer'}),
            'company':     forms.TextInput(attrs={'placeholder': 'e.g. Google'}),
            'location':    forms.TextInput(attrs={'placeholder': 'e.g. New York, USA or Remote'}),
            'start_date':  forms.DateInput(attrs={'type': 'date'}),
            'end_date':    forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe your key responsibilities and achievements…',
            }),
        }

    def clean(self):
        cleaned = super().clean()
        sd = cleaned.get('start_date')
        ed = cleaned.get('end_date')
        is_current = cleaned.get('is_current')
        if not is_current and ed and sd and ed < sd:
            self.add_error('end_date', 'End date cannot be before start date.')
        return cleaned


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = [
            'name', 'issuing_organization',
            'issue_date', 'expiry_date', 'does_not_expire',
            'credential_id', 'credential_url',
        ]
        widgets = {
            'name':                 forms.TextInput(attrs={'placeholder': 'e.g. AWS Solutions Architect'}),
            'issuing_organization': forms.TextInput(attrs={'placeholder': 'e.g. Amazon Web Services'}),
            'issue_date':           forms.DateInput(attrs={'type': 'date'}),
            'expiry_date':          forms.DateInput(attrs={'type': 'date'}),
            'credential_id':        forms.TextInput(attrs={'placeholder': 'Certificate ID (optional)'}),
            'credential_url':       forms.URLInput(attrs={'placeholder': 'https://verify.example.com/…'}),
        }
