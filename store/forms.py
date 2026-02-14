from django import forms

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Street Address'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    zip_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Zip Code'}))