from django import forms
from .models import Application


class ApplyForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': (
                    'Optional: Introduce yourself, explain why you are a great fit, '
                    'or highlight any relevant experience...'
                ),
            }),
        }
        labels = {
            'cover_letter': 'Cover Letter',
        }
