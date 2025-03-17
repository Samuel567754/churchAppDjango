from django import forms
from django.core.validators import RegexValidator
from .models import Contact

class ContactForm(forms.ModelForm):
    phone = forms.CharField(
        required=False,  # Allow empty phone numbers
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$', 
                message="Enter a valid phone number (e.g., +233123456789 or 0241234567)."
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., +233123456789 or 0241234567'})
    )

    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email', 'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Message', 'class': 'form-control', 'rows': 4}),
        }
