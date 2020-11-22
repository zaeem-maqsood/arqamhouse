
from django import forms
from .models import Recipient


class RecipientForm(forms.ModelForm):

    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Full Name"}), required=True, max_length=30)
    address = forms.CharField(label="Address", widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off", "placeholder": "123 Main Street", "id": "main_address"}), required=False)
    apt_number = forms.CharField(label="Apt Number", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "", "id": "apt_number"}), required=False)
    street_number = forms.CharField(label="Address", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "123", "id": "street_number"}), required=True)
    route = forms.CharField(label="Address", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Main Street", "id": "route"}), required=True)
    locality = forms.CharField(label="Address", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Toronto", "id": "locality"}), required=True)
    administrative_area_level_1 = forms.CharField(label="Address", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "ON", "id": "administrative_area_level_1", "maxlength": "2"}), required=True)
    postal_code = forms.CharField(label="Address", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "L1Z 5G5", "id": "postal_code"}), required=True)

    class Meta():
        model = Recipient
        fields = [
            "name",
            "address",
            "apt_number",
            "street_number",
            "route",
            "locality",
            "administrative_area_level_1",
            "postal_code",
        ]
