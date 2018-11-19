
from django import template
from django.http import HttpResponse
from django.utils.html import escape, mark_safe

register = template.Library()

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



# ----------------------------------------- Get Custom Ticket Question --------------------------------------------------
@register.simple_tag
def get_question_related_form_field(form, question):
	print(question.id)
	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(question.id) and field.name.split('_')[1] == "question":
				return field
			else:
				pass
		except:
			pass




# Get ticket question error
@register.simple_tag
def get_question_related_form_field_error(form, question):

	for field in form:
		try:
			if int(field.name.split('_')[0]) == int(question.id) and field.name.split('_')[1] == "question":
				if field.errors:
					return create_errors_string(field)
				else:
					return ""
			else:
				pass
		except:
			pass










