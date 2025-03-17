# your_app/forms.py
from django import forms
from .models import PrayerRequest
from django.contrib.auth.models import User
from .models import Member
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.forms import modelformset_factory
from .models import Appointment
from membership.models import Member



class PrayerRequestForm(forms.ModelForm):
    class Meta:
        model = PrayerRequest
        fields = ['request']  # Only the request field is needed
        widgets = {
            'request': forms.Textarea(attrs={
                'rows': 4,
                'class': (
                    'w-full border border-gray-300 dark:border-gray-600 '
                    'rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 '
                    'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                )
            }),
        }
        
        

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        # Ensure you include all fields you wish to style; if 'lord_supper_helpers'
        # and 'ushers' exist on your model, add them here.
        fields = ['member', 'role', 'day', 'date', 'status', 'reason' ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': (
                    'w-full border border-gray-300 dark:border-gray-600 rounded-md p-2 '
                    'focus:outline-none focus:ring-2 focus:ring-blue-500 '
                    'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                )
            }),
            'status': forms.Select(attrs={
                'class': (
                    'w-full border border-gray-300 dark:border-gray-600 rounded-md p-2 '
                    'focus:outline-none focus:ring-2 focus:ring-blue-500 '
                    'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                )
            }),
            'reason': forms.Select(attrs={
                'class': (
                    'w-full border border-gray-300 dark:border-gray-600 rounded-md p-2 '
                    'focus:outline-none focus:ring-2 focus:ring-blue-500 '
                    'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                )
            }),
            
        }


# Formset for bulk assigning roles
AppointmentFormSet = modelformset_factory(
    Appointment,
    form=AppointmentForm,
    extra=5,  # Number of empty forms to display
)




class AppointmentResponseForm(forms.ModelForm):
    """Form for approving or rejecting an appointment"""
    class Meta:
        model = Appointment
        fields = ['status', 'reason']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['reason'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Required if rejecting...'})

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        reason = cleaned_data.get('reason')

        if status == Appointment.STATUS_DENIED and not reason:
            self.add_error('reason', 'A reason is required when rejecting an appointment.')

        return cleaned_data
