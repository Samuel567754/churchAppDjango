from django import forms
from .models import Family, Member

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['family_name', 'address', 'phone_number', 'head_of_family']
        widgets = {
            'family_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50',
                'placeholder': 'Enter family name'
            }),
            'address': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50',
                'placeholder': 'Enter address',
                'rows': 3
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50',
                'placeholder': 'Enter phone number'
            }),
            'head_of_family': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50'
            }),
        }
        
class FamilyMemberForm(forms.Form):
    member = forms.ModelChoiceField(
        queryset=Member.objects.all(),
        help_text="Select a member to add",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50'
        })
    )
