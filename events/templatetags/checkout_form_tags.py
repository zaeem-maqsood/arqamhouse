from django import template
from events.models import EventQuestion, EventCart, EventCartItem
from questions.models import MultipleChoice
from django.http import HttpResponse
from django.utils.html import escape, mark_safe

register = template.Library()

from events.models import Ticket, EventQuestion








@register.filter(name='quantity') 
def quantity(number):
    return range(number)


@register.filter(name='ticket_question') 
def ticket_question(cart_item):
    event_questions = EventQuestion.objects.filter(tickets__id=cart_item.ticket.id, question__deleted=False, question__approved=True).order_by("question__order")
    return event_questions


@register.filter(name='multiple_choice_option')
def multiple_choice_option(question):
    multiple_choice_options = MultipleChoice.objects.filter(question=question, deleted=False)
    return multiple_choice_options










# Gets a query of all the order questions when the event is given.
# Used in the buyer questions area
@register.filter(name='order_question') 
def order_question(event):
    order_questions = EventQuestion.objects.filter(
        event=event, order_question=True, question__deleted=False, question__approved=True).order_by("question__order")
    return order_questions

# Return an error message if any of the buyer custom questions are incorrect
@register.simple_tag
def order_question_errors(errors, order_question):
    for error in errors:
        try:
            if errors["%s_order_question" % (order_question.question.id)]:
                return f""" 
                    <div class="row" style="padding-top:20px;">
                        <div class="col-md-12">
                            <div class="alert bg--error" style="margin-bottom: 3px;padding: 10px;">
                                <div class="alert__body">
                                    <span>{errors["%s_order_question" % (order_question.question.id)]}</span></div>
                            </div>
                        </div>
                    </div>
                """
            else:
                pass
        except:
            pass
    return ""




@register.simple_tag
def get_order_question_initial_value(data, order_question_id):
    try:
        value = data["%s_order_question" % order_question_id]
        return value
    except Exception as e:
        return ""

@register.simple_tag
def get_order_question_initial_value_multiplechoice(data, order_question_id, option):
    try:
        value = data["%s_order_question" % order_question_id]
        if option.title == value:
            return "selected"
        else:
            return ""
    except Exception as e:
        return ""









@register.simple_tag
def get_attendee_name_initial_value(data, quantity, ticket_id):
    try:
        value = data["%s_%s_name" % (quantity, ticket_id)]
        return value
    except Exception as e:
        return ""

@register.simple_tag
def attendee_name_error(errors, quantity, ticket_id):
    for error in errors:
        try:
            if errors["%s_%s_name" % (quantity, ticket_id)]:
                return f""" 
                    <div class="row" style="padding-top:20px;">
                        <div class="col-md-12">
                            <div class="alert bg--error" style="margin-bottom: 3px;padding: 10px;">
                                <div class="alert__body">
                                    <span>{errors["%s_%s_name" % (quantity, ticket_id)]}</span></div>
                            </div>
                        </div>
                    </div>
                """
            else:
                pass
        except:
            pass
    return ""



@register.simple_tag
def get_attendee_email_initial_value(data, quantity, ticket_id):
    try:
        value = data["%s_%s_email" % (quantity, ticket_id)]
        return value
    except Exception as e:
        return ""


@register.simple_tag
def get_attendee_address_initial_value(data, quantity, ticket_id):
    try:
        value = data["%s_%s_address" % (quantity, ticket_id)]
        return value
    except Exception as e:
        return ""

@register.simple_tag
def attendee_address_error(errors, quantity, ticket_id):
    for error in errors:
        try:
            if errors["%s_%s_address" % (quantity, ticket_id)]:
                return f""" 
                    <div class="row" style="padding-top:20px;">
                        <div class="col-md-12">
                            <div class="alert bg--error" style="margin-bottom: 3px;padding: 10px;">
                                <div class="alert__body">
                                    <span>{errors["%s_%s_address" % (quantity, ticket_id)]}</span></div>
                            </div>
                        </div>
                    </div>
                """
            else:
                pass
        except:
            pass
    return ""





@register.simple_tag
def get_attendee_age_initial_value(data, quantity, ticket_id):
    try:
        value = data["%s_%s_age" % (quantity, ticket_id)]
        return value
    except Exception as e:
        return ""

@register.simple_tag
def attendee_age_error(errors, quantity, ticket_id):
    for error in errors:
        try:
            if errors["%s_%s_age" % (quantity, ticket_id)]:
                return f""" 
                    <div class="row" style="padding-top:20px;">
                        <div class="col-md-12">
                            <div class="alert bg--error" style="margin-bottom: 3px;padding: 10px;">
                                <div class="alert__body">
                                    <span>{errors["%s_%s_age" % (quantity, ticket_id)]}</span></div>
                            </div>
                        </div>
                    </div>
                """
            else:
                pass
        except:
            pass
    return ""


@register.simple_tag
def get_attendee_gender_initial_value(data, quantity, ticket_id, gender):
    try:
        value = data["%s_%s_gender" % (quantity, ticket_id)]
        if gender == value:
            return "selected"
        else:
            return ""
    except Exception as e:
        return ""




@register.simple_tag
def get_attendee_question_initial_value(data, quantity, question_id, ticket_id):
    try:
        value = data["%s_%s_%s" % (quantity, question_id, ticket_id)]
        return value
    except Exception as e:
        return ""

@register.simple_tag
def attendee_question_error(errors, quantity, question_id, ticket_id):
    for error in errors:
        try:
            if errors["%s_%s_%s" % (quantity, question_id, ticket_id)]:
                return f""" 
                    <div class="row" style="padding-top:20px;">
                        <div class="col-md-12">
                            <div class="alert bg--error" style="margin-bottom: 3px;padding: 10px;">
                                <div class="alert__body">
                                    <span>{errors["%s_%s_%s" % (quantity, question_id, ticket_id)]}</span></div>
                            </div>
                        </div>
                    </div>
                """
            else:
                pass
        except:
            pass
    return ""





@register.simple_tag
def get_attendee_question_initial_value_multiplechoice(data, quantity, question_id, ticket_id, option):
    try:
        value = data["%s_%s_%s" % (quantity, question_id, ticket_id)]
        if option.title == value:
            return "selected"
        else:
            return ""
    except Exception as e:
        return ""
