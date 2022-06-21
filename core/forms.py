from django import forms
from .models import *
from django.contrib.auth import get_user_model


class AddItemToCartForm(forms.Form):
    n_pieces = forms.IntegerField(min_value=1, max_value=99, initial=1)


class AddressForm(forms.ModelForm):
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


class NoLabelsModelForm(forms.ModelForm):
    """
    Base class for ModelForm without field labels.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in self.Meta.fields:
            self.fields[fieldname].help_text = None


class CustomerForm(NoLabelsModelForm):

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

        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"})
        }


class EmailForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["email"]


class CustomerCheckoutForm(CustomerForm):

    class Meta:
        model = Customer
        fields = ["first_name", "second_name", "last_name", "phone_number"]

        labels = {
            "first_name": "Imię",
            "second_name": "Drugie imię",
            "last_name": "Nazwisko",
            "phone_number": "Numer telefonu",
        }


class OrderMethodsForm(NoLabelsModelForm):

    class Meta:
        model = Order
        fields = ["delivery_method", "payment_method"]
