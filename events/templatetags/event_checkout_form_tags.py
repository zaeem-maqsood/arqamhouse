from django import template
from carts.models import EventCart, EventCartItem
from questions.models import EventQuestion, AllTicketQuestionControl, TicketQuestion
from django.http import HttpResponse
from django.utils.html import escape, mark_safe

register = template.Library()


@register.simple_tag
def get_attendee_related_form_field(form, attendee):

	print()
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(attendee.id) and field.name.split('_')[1] == "attendee":
				print("This is the id")
				print(attendee.id)
				return field
			else:
				pass
		except Exception as e:
			print(e)
			pass


def create_errors_string(field):
	error_string = ""
	for error in field.errors:
		sub_error_string = """
							<div class="col-md-12">
						        <div class="alert bg--error">
									<div class="alert__body">
										Oh snap! The field "%s" has errors. %s
									</div>
									<div class="alert__close">×</div>
								</div>
							</div>
							<br>
							""" % (field.label, error)
		error_string += sub_error_string
	return error_string


@register.simple_tag
def get_event_question_related_form_field(form, event_question):

	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(event_question.id) and field.name.split('_')[1] == "eventquestion":
				return field
			else:
				pass
		except:
			pass
			

@register.simple_tag
def get_event_question_related_form_field_error(form, event_question):

	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(event_question.id) and field.name.split('_')[1] == "eventquestion":
				if field.errors:
					return create_errors_string(field)
				else:
					return ""
			else:
				pass
		except: 
			pass




# First Name Errors 
@register.simple_tag
def get_ticket_name_form_field_errors(form, cart_item, quantity):
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(quantity) and int(field.name.split('_')[1]) == int(cart_item.id) and field.name.split('_')[2] == "name":
				if field.errors:
					return create_errors_string(field)
				else:
					return ""
			else:
				pass
		except:
			pass

# First Name Field
@register.simple_tag
def get_ticket_name_form_field(form, cart_item, quantity):
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(quantity) and int(field.name.split('_')[1]) == int(cart_item.id) and field.name.split('_')[2] == "name":
				return field
			else:
				pass
		except:
			pass



# Email Errors
@register.simple_tag
def get_ticket_email_form_field_errors(form, cart_item, quantity):
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(quantity) and int(field.name.split('_')[1]) == int(cart_item.id) and field.name.split('_')[2] == "email":
				if field.errors:
					return create_errors_string(field)
				else:
					return ""
			else:
				pass
		except:
			pass

# Email Field
@register.simple_tag
def get_ticket_email_form_field(form, cart_item, quantity):
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(quantity) and int(field.name.split('_')[1]) == int(cart_item.id) and field.name.split('_')[2] == "email":
				return field
			else:
				pass
		except:
			pass





# Gender Field
@register.simple_tag
def get_ticket_gender_form_field(form, cart_item, quantity):
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(quantity) and int(field.name.split('_')[1]) == int(cart_item.id) and field.name.split('_')[2] == "gender":
				return field
			else:
				pass
		except:
			pass

# --------------------------- Gender Field options ---------------------------------------------------------
@register.simple_tag
def get_ticket_gender_option_form_field(form, cart_item, quantity, counter):
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(quantity) and int(field.name.split('_')[1]) == int(cart_item.id) and field.name.split('_')[2] == "gender":
				return field[counter]
			else:
				pass
		except:
			pass

# Name Value
@register.simple_tag
def get_ticket_gender_option_form_field_name(form, cart_item, quantity, counter):
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(quantity) and int(field.name.split('_')[1]) == int(cart_item.id) and field.name.split('_')[2] == "gender":
				print(field[counter].data)
				return field[counter].data["name"]
			else:
				pass
		except:
			pass

# Id Value
@register.simple_tag
def get_ticket_gender_option_form_field_id(form, cart_item, quantity, counter):
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(quantity) and int(field.name.split('_')[1]) == int(cart_item.id) and field.name.split('_')[2] == "gender":
				return field[counter].id_for_label
			else:
				pass
		except:
			pass

# Value Value
@register.simple_tag
def get_ticket_gender_option_form_field_value(form, cart_item, quantity, counter):
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(quantity) and int(field.name.split('_')[1]) == int(cart_item.id) and field.name.split('_')[2] == "gender":
				return field[counter].data["value"]
			else:
				pass
		except:
			pass

# Selected Value
@register.simple_tag
def get_ticket_gender_option_form_field_checked(form, cart_item, quantity, counter):
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(quantity) and int(field.name.split('_')[1]) == int(cart_item.id) and field.name.split('_')[2] == "gender":
				return field[counter].data["selected"]
			else:
				pass
		except:
			pass

# Label Value
@register.simple_tag
def get_ticket_gender_option_form_field_label(form, cart_item, quantity, counter):
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(quantity) and int(field.name.split('_')[1]) == int(cart_item.id) and field.name.split('_')[2] == "gender":
				return field[counter].data["label"]
			else:
				pass
		except:
			pass





# ----------------------------------------- Get Custom Ticket Question --------------------------------------------------
@register.simple_tag
def get_ticket_question_related_form_field(form, ticket_question, cart_item, quantity):
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(ticket_question.id) and int(field.name.split('_')[1]) == int(quantity) and int(field.name.split('_')[2]) == int(cart_item.id):
				return field
			else:
				pass
		except:
			pass




# Get ticket question error
@register.simple_tag
def get_ticket_question_related_form_field_error(form, ticket_question, cart_item, quantity):

	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(ticket_question.id) and int(field.name.split('_')[1]) == int(quantity) and int(field.name.split('_')[2]) == int(cart_item.id):
				if field.errors:
					return create_errors_string(field)
				else:
					return ""
			else:
				pass
		except:
			pass





















