# blog/forms.py
from django import forms
from .models import Post, Comment



class CommentForm(forms.ModelForm):
    """
    Form for posting comments
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment here...'}),
        }