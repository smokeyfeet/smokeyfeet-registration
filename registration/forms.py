from django import forms
from django.forms import widgets

from .models import Registration


class SignupForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = ('first_name', 'last_name', 'email', 'dance_role',
                'telephone', 'country_of_residence', 'wants_volunteer',
                'pass_type', 'workshop_partner')
        widgets = {
                'dance_role': forms.widgets.RadioSelect(),
                'pass_type': forms.widgets.RadioSelect()}


class CompletionForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = ('wants_lunch',)
