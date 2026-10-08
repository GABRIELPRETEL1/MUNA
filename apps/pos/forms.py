from django import forms


class SaleCheckoutForm(forms.Form):
    payment_method = forms.ChoiceField(choices=[('cash', 'Efectivo'), ('card', 'Tarjeta'), ('transfer', 'Transferencia')])
