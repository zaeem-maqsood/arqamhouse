from django import template
from events.models import EventQuestion, EventCart, EventCartItem
from questions.models import MultipleChoice
from django.http import HttpResponse
from django.utils.html import escape, mark_safe

register = template.Library()


@register.simple_tag
def get_name_error_message(form, field, iteration):
    for x in form:
        if x.name == f"{iteration}_{field}":
            if x.errors:
                error_message = f"""
                <div class="row" style="padding-top:10px;">
                    <div class="col-md-12">
                        <div class="alert bg--error">
                            <div class="alert__body">
                                
                                <span>{x.errors}</span>
                                
                            </div>
                        </div>
                    </div>
                </div>
                """
                return error_message
    return ""

@register.simple_tag
def get_name_value(form, field, iteration):
    try:
        value = form.cleaned_data.get(f"{iteration}_{field}")
        if value:
            return value
        else:
            return ""
    except Exception as e:
        print(e)
        return ""





@register.simple_tag
def get_autocomplete_value(form, field, iteration):
    try:
        value = form.cleaned_data.get(f"{field}{iteration}")
        if value:
            return value
        else:
            return ""
    except Exception as e:
        print(e)
        return ""







@register.simple_tag
def get_address_error_message(form, field, iteration):
    for x in form:
        if x.name == f"{field}_{iteration}":
            if x.errors:
                error_message = f"""
                    <div class="alert bg--error" style="margin-top:10px;">
                        <div class="alert__body">
                            <span>{x.errors}</span>
                        </div>
                    </div>
                """
                return error_message
    return ""


@register.simple_tag
def get_address_values(form, field, iteration):
    try:
        value = form.cleaned_data.get(f"{field}_{iteration}")
        if value:
            return value
        else:
            return ""
    except Exception as e:
        print(e)
        return ""
