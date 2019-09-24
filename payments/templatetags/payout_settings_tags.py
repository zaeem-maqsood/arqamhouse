from django import template
from payments.models import PayoutSetting
from django.shortcuts import render
from django.template.response import TemplateResponse

register = template.Library()



@register.simple_tag
def get_institution_logo(request, payout_setting):
    try:
        print(dir(TemplateResponse(request, "payments/bank_images/%s.html" %
                             (payout_setting.bank_transfer.institution))))
        return TemplateResponse(request, "payments/bank_images/%s.html" % (payout_setting.bank_transfer.institution))
    except Exception as e:
        print(e)
        return ""
