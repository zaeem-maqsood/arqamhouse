from django import forms
from .models import Etransfer, PayoutSetting


class AddEtransferForm(forms.ModelForm):


    class Meta:
        model = Etransfer
        fields = [
            "email",
            "password",
        ]


        widgets = {
            "email": forms.EmailInput(
                    attrs={
                        "class":"form-control m-input",
                        "placeholder":"example@example.com",
                        "required": True
                    }
                ),
            "password": forms.TextInput(
                    attrs={
                        "class":"form-control m-input",
                        "placeholder":"password",
                         "oninput" : "this.value=this.value.toLowerCase()",
                        "required": True
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
        