from django import forms
from django.core.validators import ValidationError
from .models import CartItem


class AddItemToCartForm(forms.Form):
    n_pieces = forms.IntegerField(min_value=1, max_value=99, label="Number of pieces")
