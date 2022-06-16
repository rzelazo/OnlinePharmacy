from django import forms
from .models import Address


class AddItemToCartForm(forms.Form):
    n_pieces = forms.IntegerField(min_value=1, max_value=99)


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = "__all__"
        labels = {
            "country": "Kraj",
            "city": "Miasto",
            "street": "Ulica",
            "street_number": "Numer domu",
            "local_number": "Numer lokalu",
            "postal_code": "Kod pocztowy"
        }
