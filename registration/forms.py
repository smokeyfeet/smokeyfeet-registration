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

    email_repeat = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['pass_type'].empty_label = None

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()
        email = cleaned_data.get("email")
        email_repeat = cleaned_data.get("email_repeat")

        if email != email_repeat:
            raise forms.ValidationError("Ensure email verfication matches")


class CompletionForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = ('include_lunch', 'diet_requirements', 'competitions',
                'strictly_partner', 'volunteering_for', 'agree_to_terms')

        widgets = {
                'competitions': forms.widgets.CheckboxSelectMultiple(),
                'volunteering_for': forms.widgets.CheckboxSelectMultiple()}

    def clean_agree_to_terms(self):
        data = self.cleaned_data['agree_to_terms']
        if data is False:
            raise forms.ValidationError("You must agree to the terms")
        return data

    def clean(self):
        cleaned_data = super(CompletionForm, self).clean()
        competitions = cleaned_data.get("competitions")
        strictly_partner = cleaned_data.get("strictly_partner")

        require_partner = any([c.require_partner for c in competitions])

        if require_partner and not strictly_partner:
            raise forms.ValidationError("Competition requires partner")
