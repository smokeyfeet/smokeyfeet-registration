from django import forms

from .models import Registration


class SignupForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = ('first_names', 'last_name', 'email', 'is_lead', 'telephone',
                'country', 'workshop_level', 'workshop_partner')


class CompletionForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = ('wants_lunch',)
