
from django import forms

from donations.models import Donation, DonationType


class DonationTypeForm(forms.ModelForm):


    class Meta:
        model = DonationType
        fields = [
            "name", "pass_fee", "issue_receipts", "collect_address", "description"
        ]

        widgets = {

                "name": forms.TextInput(
                        attrs={
                            "class": "form-control m-input",
                            "placeholder":"i.e. Food Drive Donations",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),

                "description": forms.Textarea(
                    attrs={
                        "class": "form-control m-input",
                        "placeholder": "What will these donations be used for?",
                        "required": True,
                        "maxlength": '150',
                        "rows": "3"
                    }
                ),

                "pass_fee": forms.CheckboxInput(),
                "issue_receipts": forms.CheckboxInput(),
                "collect_address": forms.CheckboxInput(),
        }







class DonationForm(forms.ModelForm):

    amount = forms.DecimalField(widget=forms.NumberInput(attrs={"class": "validate-required", "min": "5.00", "max": "5000.00",
                                                                "step": "1.00", "value": "20.00", "required": True, "onchange": "showAddressAndFee(document.getElementById('id_donation_type'));updateAmount(document.getElementById('id_donation_type'));"}))

    def __init__(self, house, *args, **kwargs):
        super(DonationForm, self).__init__(*args, **kwargs)

        donation_types = DonationType.objects.filter(house=house)

        self.fields["donation_type"] = forms.ModelChoiceField(queryset=donation_types, empty_label=None, widget=forms.Select(
            attrs={"class": "validate-required", "onchange": "showAddressAndFee(this);"}), required=True, initial=DonationType.objects.get(house=house, general_donation=True))
        self.fields["address"] = forms.CharField(label="Address", widget=forms.TextInput(attrs={"class":"validate-required", "autocomplete": "off", "placeholder": "123 Main Street", "id": "autocomplete"}), required=False)


    class Meta:
        model = Donation
        fields = [
            "name", "email", "amount", "message", "anonymous"
        ]

        widgets = {

                "name": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder":"Full Name",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),

                "message": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder":"Give a dua with your donation...",
                            "required": False,
                            "maxlength": '100',
                        }
                    ),

                "email": forms.EmailInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder": "someone@example.com",
                            "required": True,
                            "maxlength": '200',
                        }
                    ),

                "anonymous": forms.CheckboxInput(),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount:
            if amount < 5.00:
                raise forms.ValidationError('Please donate a minimum of $5.00')
            else:
                return amount
        else:
            return logo


    def clean_address(self):
        donation_type = self.cleaned_data.get('donation_type')
        address = self.cleaned_data.get('address')

        if donation_type.collect_address:
            if donation_type and address:
                if donation_type.collect_address and not address:
                    raise forms.ValidationError('Please enter and address')
                else:
                    return address
            else:
                raise forms.ValidationError('No Donation Type Selected')









class GiftDonationForm(forms.ModelForm):

    amount = forms.DecimalField(widget=forms.NumberInput(attrs={"class": "validate-required", "min": "5.00", "max": "5000.00",
                                                                "step": "1.00", "value": "20.00", "required": True, "onchange": "showAddressAndFee(document.getElementById('id_donation_type'));"}))

    def __init__(self, house, *args, **kwargs):
        super(GiftDonationForm, self).__init__(*args, **kwargs)

        donation_types = DonationType.objects.filter(house=house)

        self.fields["donation_type"] = forms.ModelChoiceField(queryset=donation_types, empty_label=None, widget=forms.Select(
            attrs={"class": "validate-required", "onchange": "showAddressAndFee(this);"}), required=True, initial=DonationType.objects.get(house=house, general_donation=True))
        self.fields["address"] = forms.CharField(label="Address", widget=forms.TextInput(attrs={"class":"validate-required", "autocomplete": "off", "placeholder": "123 Main Street", "id": "autocomplete"}), required=False)
        self.fields["recipient_address"] = forms.CharField(label="Recipient Address", widget=forms.TextInput(attrs={"class":"validate-required", "autocomplete": "off", "placeholder": "123 Main Street", "id": "autocomplete2"}), required=False)

    class Meta:
        model = Donation
        fields = [
            "name", "email", "amount", "message", "anonymous", "message_to_recipient", "recipient_name", "recipient_email", 
            "recipient_postal_code", "send_e_card"
        ]

        widgets = {

                "name": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder":"Full Name",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),

                "recipient_name": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder":"Recipient Full Name",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),

                "recipient_postal_code": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder":"L1Z 5J5",
                            "required": True,
                            "maxlength": '7',
                        }
                    ),

                "message": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder":"Give a dua with your donation",
                            "required": False,
                            "maxlength": '100',
                        }
                    ),

                "message_to_recipient": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder":"Give a personalized message with your gift",
                            "required": False,
                            "maxlength": '150',
                        }
                    ),

                "email": forms.EmailInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder": "someone@example.com",
                            "required": True,
                            "maxlength": '200',
                        }
                    ),

                
                "recipient_email": forms.EmailInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder": "someone@example.com",
                            "required": True,
                            "maxlength": '200',
                        }
                    ),

                "anonymous": forms.CheckboxInput(
                    attrs={
                        "checked": True,
                    }
                ),

                "send_e_card": forms.CheckboxInput(
                    attrs={
                        "checked": True,
                    }
                ),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount:
            if amount < 5.00:
                raise forms.ValidationError('Please donate a minimum of $5.00')
            else:
                return amount
        else:
            return logo


    def clean_address(self):
        donation_type = self.cleaned_data.get('donation_type')
        address = self.cleaned_data.get('address')

        if donation_type.collect_address:
            if donation_type and address:
                if donation_type.collect_address and not address:
                    raise forms.ValidationError('Please enter and address')
                else:
                    return address
            else:
                raise forms.ValidationError('No Donation Type Selected')
