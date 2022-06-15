from django import forms


class AddItemToCartForm(forms.Form):
    n_pieces = forms.IntegerField(min_value=1, max_value=99)
