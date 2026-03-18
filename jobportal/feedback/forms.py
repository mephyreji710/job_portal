from django import forms
from .models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model   = Feedback
        fields  = ['rating', 'comment', 'is_anonymous']
        widgets = {
            'rating':  forms.HiddenInput(),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Share your experience (optional)…',
            }),
        }
        labels = {
            'comment':      'Your Review',
            'is_anonymous': 'Post anonymously',
        }
