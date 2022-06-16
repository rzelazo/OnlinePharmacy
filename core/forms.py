from django import forms
from .models import *


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


class CustomerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in self.Meta.fields:
            self.fields[fieldname].help_text = None

    class Meta:
        model = Customer
        fields = ["first_name", "second_name", "last_name",
                  "date_of_birth", "phone_number", "gender"]

        labels = {
            "first_name": "Imię",
            "second_name": "Drugie imię",
            "last_name": "Nazwisko",
            "date_of_birth": "Data urodzenia",
            "phone_number": "Numer telefonu",
            "gender": "Płeć"
        }