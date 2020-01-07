from django import forms


class ReportErrorForm(forms.Form):

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"required" : True, "class":"validate-required", "placeholder": "Email"}))
    name = forms.CharField(required=True, strip=True, widget=forms.TextInput(attrs={"required": True, "class": "validate-required", "placeholder": "Name"}))
    message = forms.CharField(required=True, strip=True, widget=forms.Textarea(attrs={"required": True, "class": "validate-required", "placeholder": "Message"}))