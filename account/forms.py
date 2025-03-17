# your_app/forms.py
from django import forms
from django.contrib.auth.models import User
from membership.models import Member, Membership, Family, Attendance, Ministry
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.forms import PasswordResetForm



class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(
        self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None
    ):
        subject = render_to_string(subject_template_name, context).strip()
        text_content = render_to_string(email_template_name, context)

        # ✅ Render HTML Email Properly with Context
        html_content = render_to_string("account/emails/password_reset_email.html", context)

        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, "text/html")  # ✅ Attach HTML content
        email.send()

        
     
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        

# UserRegistrationForm for new user registration with password confirmation
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
    }))
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError('Password must contain at least one digit.')
        if not any(char.isalpha() for char in password):
            raise forms.ValidationError('Password must contain at least one letter.')
        return password

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
        }
        
        def clean_username(self):
            username = self.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('This username is already taken.')
            return username
        
        
        def clean_email(self):
            email = self.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('This email is already in use.')
            return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


# MemberProfileForm for additional member profile details
class MemberProfileForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
        })
    )
    photo = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'mt-1 block w-full',
        })
    )
    # Set date_of_birth as required
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
        }),
        required=True
    )
    
    ministries = forms.ModelMultipleChoiceField(
        queryset=Ministry.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'mt-1',
        }),
        required=False
    )

    class Meta:
        model = Member
        fields = ['phone', 'address', 'date_of_birth', 'photo', 'gender', 'baptized', 'can_lead', 'ministries']
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'gender': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'baptized': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded',
            }),
            'can_lead': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded',
            }),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone




class MemberLoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))