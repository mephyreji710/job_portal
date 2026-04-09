from django import forms
from .models import Task, TaskSubmission


class AssignTaskForm(forms.ModelForm):
    class Meta:
        model  = Task
        fields = ['title', 'description', 'attachment_type', 'attachment', 'attachment_url', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Write a Blog Article',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Describe the task requirements, goals, and any specific instructions…',
                'class': 'form-control',
            }),
            'attachment_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_attachment_type'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control', 'id': 'id_attachment_file'}),
            'attachment_url': forms.URLInput(attrs={
                'placeholder': 'https://…',
                'class': 'form-control',
                'id': 'id_attachment_url',
            }),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class TaskSubmissionForm(forms.ModelForm):
    class Meta:
        model  = TaskSubmission
        fields = ['submission_text', 'submission_file']
        widgets = {
            'submission_text': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Describe your work, explain your approach, or paste relevant content here…',
                'class': 'form-control',
            }),
            'submission_file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ReviewTaskForm(forms.Form):
    action   = forms.ChoiceField(choices=[('approved', 'Approve'), ('rejected', 'Reject')])
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Optional feedback for the candidate…',
            'class': 'form-control',
        })
    )
