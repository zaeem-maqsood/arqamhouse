from django import forms
from .models import PayoutSetting


class AddBankTransferForm(forms.ModelForm):

    class Meta:
        model = PayoutSetting
        fields = [
            "name", "official_document",
        ]


        widgets = {
            "name": forms.TextInput(
                attrs={
                    "required": True,
                    "placeholder": "Account Name i.e. 'Events Account",
                    "class": "form-control m-input",
                }
            ),

            "official_document": forms.FileInput(
                attrs={
                    "required": True,
                    "class": "form-control m-input",
                }
            ),
        }


class AddFundsForm(forms.Form):

    amount = forms.DecimalField(widget=forms.NumberInput(attrs={"class":"form-control m-input", "min" : "1.00", "max": "2000.00", "step": "0.01", "value": "5.00", "required": True, "onkeyup": "updateFeeAndTotal(this)", "autofocus": "True"}))



class PayoutForm(forms.Form):

    amount = forms.DecimalField(widget=forms.NumberInput(attrs={"class":"form-control m-input", "min" : "1.00", "max": "2000.00", "step": "0.01", "value": "0.00", "required": True, "onkeyup": "updateFeeAndTotal(this)", "autofocus": "True"}))

    def __init__(self, total, house, *args, **kwargs):
        
        print(total)
        super(PayoutForm, self).__init__(*args, **kwargs)
        self.fields["amount"] =  forms.DecimalField(widget=forms.NumberInput(attrs={"class":"form-control m-input", "min" : "1.00", "max": "%s" % (total), "step": "0.01", "value": "0.00", "required": True, "onkeyup": "updateFeeAndTotal(this)", "autofocus": "True"}))
        self.fields["payout_setting"] = forms.ModelChoiceField(queryset=PayoutSetting.objects.filter(house=house), empty_label=None, widget=forms.Select(attrs={"class":"form-control m-input", "required": True}))
    
