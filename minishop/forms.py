from django import forms

from .models import Order


class AddProductForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('email', 'first_name', 'last_name')
