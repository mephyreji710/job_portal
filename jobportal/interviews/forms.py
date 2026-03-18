from django import forms
from .models import Interview


class ScheduleInterviewForm(forms.ModelForm):
    scheduled_at = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'},
            format='%Y-%m-%dT%H:%M',
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Date & Time',
    )

    class Meta:
        model = Interview
        fields = ['scheduled_at', 'duration_mins', 'interview_type',
                  'location', 'meeting_link', 'notes']
        widgets = {
            'duration_mins':  forms.Select(
                choices=[(30, '30 min'), (45, '45 min'), (60, '1 hour'),
                         (90, '1.5 hours'), (120, '2 hours')],
                attrs={'class': 'form-control'}),
            'interview_type': forms.Select(attrs={'class': 'form-control'}),
            'location':       forms.TextInput(attrs={'class': 'form-control',
                               'placeholder': 'e.g. Office address or "Google Meet"'}),
            'meeting_link':   forms.URLInput(attrs={'class': 'form-control',
                               'placeholder': 'https://meet.google.com/...'}),
            'notes':          forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                               'placeholder': 'Preparation tips, what to bring, agenda...'}),
        }
        labels = {
            'duration_mins':  'Duration',
            'interview_type': 'Interview Type',
            'location':       'Location / Platform',
            'meeting_link':   'Meeting Link',
            'notes':          'Message to Candidate',
        }
