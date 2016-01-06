from django import forms

from .models import Registration


class SignupForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = (
                'first_name', 'last_name', 'email', 'dance_role',
                'pass_type', 'workshop_partner_name', 'workshop_partner_email')
        widgets = {
                'dance_role': forms.widgets.RadioSelect(),
                'pass_type': forms.widgets.RadioSelect()}

    class Media:
        css = {'all': ('css/forms.css',)}

    email_repeat = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['pass_type'].empty_label = None

    def clean_workshop_partner_email(self):
        """
        Take care of uniqueness constraint ourselves
        """
        email = self.cleaned_data.get("workshop_partner_email")
        qs = Registration.objects.filter(workshop_partner_email=email).exists()
        if email and qs:
            raise forms.ValidationError("Workshop parter already taken.")

        return email

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()
        email = cleaned_data.get("email")
        email_repeat = cleaned_data.get("email_repeat")
        ws_partner_email = cleaned_data.get("workshop_partner_email")

        if email != email_repeat:
            raise forms.ValidationError("Ensure email verfication matches.")

        if email and ws_partner_email and email == ws_partner_email:
            raise forms.ValidationError("You can't partner with yourself.")


class CompletionForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = ('residing_country', 'include_lunch', 'diet_requirements',
                'competitions', 'strictly_partner', 'volunteering_for')

        widgets = {
                'diet_requirements': forms.Textarea(
                        attrs={'rows': 4, 'cols': 15}),
                'competitions': forms.widgets.CheckboxSelectMultiple(),
                'volunteering_for': forms.widgets.CheckboxSelectMultiple()}

    class Media:
        css = {'all': ('css/forms.css',)}

    agree_to_terms = forms.BooleanField(required=False)

    def clean_agree_to_terms(self):
        data = self.cleaned_data['agree_to_terms']
        if data is False:
            raise forms.ValidationError("You must agree to the terms.")
        return data

    def clean(self):
        cleaned_data = super(CompletionForm, self).clean()
        competitions = cleaned_data.get("competitions")
        strictly_partner = cleaned_data.get("strictly_partner")

        require_partner = any([c.require_partner for c in competitions])

        if require_partner and not strictly_partner:
            raise forms.ValidationError("Competition requires partner.")
