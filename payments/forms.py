from django import forms


class AddFundsForm(forms.Form):

    amount = forms.IntegerField(widget=forms.NumberInput(attrs={"class":"form-control m-input", "min" : "1.00", "max": "2000.00", "step": "0.01", "value": "5.00", "required": True, "onkeyup": "updateFeeAndTotal(this)", "autofocus": "True"}))



class PayoutForm(forms.Form):

    amount = forms.IntegerField(widget=forms.NumberInput(attrs={"class":"form-control m-input", "min" : "1.00", "max": "2000.00", "step": "0.01", "value": "5.00", "required": True, "onkeyup": "updateFeeAndTotal(this)", "autofocus": "True"}))

