from django import forms

from .models import Order


class AddProductForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ("email", "first_name", "last_name")

    email_repeat = forms.EmailField()

    def clean(self):
        cleaned_data = super(OrderForm, self).clean()

        email = cleaned_data.get("email")
        email_repeat = cleaned_data.get("email_repeat")

        if email != email_repeat:
            raise forms.ValidationError("Ensure email verification matches.")
