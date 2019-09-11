from django import template
from payments.models import PayoutSetting, Etransfer


register = template.Library()



@register.simple_tag
def get_type(instance):

    if instance.etransfer:
        return "Etransfer"