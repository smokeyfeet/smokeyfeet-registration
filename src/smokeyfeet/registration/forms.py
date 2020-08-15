from django import forms

from .models import PassType, Registration


class SignupForm(forms.ModelForm):

    pass_type = forms.ModelChoiceField(
        queryset=PassType.objects.filter(active=True),
        widget=forms.widgets.RadioSelect(),
    )

    class Meta:
        model = Registration
        fields = (
            "first_name",
            "last_name",
            "email",
            "residing_country",
            "dance_role",
            "pass_type",
            "workshop_partner_name",
            "workshop_partner_email",
            "lunch",
        )
        widgets = {
            "dance_role": forms.widgets.RadioSelect(),
            "lunch": forms.widgets.RadioSelect(),
        }

    class Media:
        css = {"all": ("css/forms.css",)}

    email_repeat = forms.EmailField()

    agree_to_terms = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields["pass_type"].empty_label = None
        self.fields["lunch"].empty_label = None

    def clean_workshop_partner_email(self):
        """
        Take care of uniqueness constraint ourselves
        """
        email = self.cleaned_data.get("workshop_partner_email")
        qs = Registration.objects.filter(workshop_partner_email=email).exists()
        if email and qs:
            raise forms.ValidationError("Workshop parter already taken.")

        return email

    def clean_agree_to_terms(self):
        data = self.cleaned_data["agree_to_terms"]
        if data is False:
            raise forms.ValidationError("You must agree to the terms.")
        return data

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        email_repeat = cleaned_data.get("email_repeat")
        ws_partner_email = cleaned_data.get("workshop_partner_email")

        if email != email_repeat:
            raise forms.ValidationError("Ensure email verfication matches.")

        if email and ws_partner_email and email == ws_partner_email:
            raise forms.ValidationError("You can't partner with yourself.")
