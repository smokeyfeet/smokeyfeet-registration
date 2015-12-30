from django import forms

from .models import Registration


class SignupForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = (
                'first_name', 'last_name', 'email', 'dance_role',
                'telephone', 'residing_country', 'pass_type',
                'workshop_partner')
        widgets = {
                'dance_role': forms.widgets.RadioSelect(),
                'pass_type': forms.widgets.RadioSelect()}


class CompletionForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = ('include_lunch', 'diet_requirements', 'volunteering_for',
                'competitions', 'strictly_partner')
