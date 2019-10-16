from .base import *

from events.models import Event, AttendeeCommonQuestions, EventCart, EventCartItem
from core.constants import genders

from froala_editor.widgets import FroalaEditor



class EventCheckoutForm(forms.Form):

	def __init__(self, event, cart, *args, **kwargs):
		
		super(EventCheckoutForm, self).__init__(*args, **kwargs)

		self.fields["email"] = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class":"validate-required"}), required=True)
		if cart.total == 0.00:
			self.fields["name"] = forms.CharField(label="Name", widget=forms.TextInput(attrs={"class":"validate-required"}), required=True)

		event_questions = EventQuestion.objects.filter(event=event, deleted=False, approved=True).order_by('order')
		for question in event_questions:
			if question.simple_question:
				self.fields["%s_eventquestion" % (question.id)] = forms.CharField(label=str(question.title), widget=forms.TextInput(attrs={"class":"validate-required"}), required=question.required)
			elif question.paragraph_question:
				self.fields["%s_eventquestion" % (question.id)] = forms.CharField(label=str(question.title), widget=forms.Textarea(attrs={"class":"validate-required", "rows": "4"}), required=question.required)
			elif question.multiple_choice_question:
				options = EventQuestionMultipleChoiceOption.objects.filter(event_question=question, deleted=False)
				choices_for_question = []
				for option in options:
					sub_list = []
					sub_list.append(option.title)
					sub_list.append(option.title)
					choices_for_question.append(sub_list)
				print(choices_for_question)
				self.fields["%s_eventquestion" % (question.id)] = forms.ChoiceField(label=str(question.title), widget=forms.Select(attrs={"class":""}), required=question.required, choices=choices_for_question)


		cart_items = EventCartItem.objects.filter(event_cart=cart)
		for cart_item in cart_items:

			for x in range(cart_item.quantity):

				attendee_general_questions = AttendeeGeneralQuestions.objects.get(event=event)

				self.fields["%s_%s_name" % (x, cart_item.id)] = forms.CharField(label="Name", widget=forms.TextInput(attrs={"class":"validate-required", "placeholder":"Full Name"}), required=True)
				
				if attendee_general_questions.gender:
					self.fields["%s_%s_gender" % (x, cart_item.id)] = forms.ChoiceField(label="Gender", widget=forms.RadioSelect(attrs={"class":""}), choices=genders)
				
				if attendee_general_questions.email:
					self.fields["%s_%s_email" % (x, cart_item.id)] = forms.EmailField(label="Email", widget=forms.TextInput(attrs={"class":"validate-required", "placeholder":"you@somedomain.com"}), required=attendee_general_questions.email_required)

				ticket_questions = TicketQuestion.objects.filter(event=event, ticket=cart_item.ticket, deleted=False, approved=True).order_by('order')
				for question in ticket_questions:
					if question.simple_question:
						self.fields["%s_%s_%s_ticketquestion" % (question.id, x, cart_item.id)] = forms.CharField(label=str(question.title), widget=forms.TextInput(attrs={"class":"validate-required"}), required=question.required)
					elif question.paragraph_question:
						self.fields["%s_%s_%s_ticketquestion" % (question.id, x, cart_item.id)] = forms.CharField(label=str(question.title), widget=forms.Textarea(attrs={"class":"validate-required", "rows": "4"}), required=question.required)
					else:
						options = TicketQuestionMultipleChoiceOption.objects.filter(ticket_question=question, deleted=False)
						choices_for_question = []
						for option in options:
							sub_list = []
							sub_list.append(option.title)
							sub_list.append(option.title)
							choices_for_question.append(sub_list)
						self.fields["%s_%s_%s_ticketquestion" % (question.id, x, cart_item.id)] = forms.ChoiceField(label=str(question.title), widget=forms.Select(attrs={"class":""}), required=question.required, choices=choices_for_question)



class EventForm(forms.ModelForm):

	start = forms.DateTimeField(input_formats=["%m/%d/%Y %I:%M %p"],  required=False, widget=forms.DateTimeInput(
		attrs={"class": "form-control m-input", "placeholder": "Start", "autocomplete": "off", "onchange": "endDateTime(this)"}))
	end = forms.DateTimeField(input_formats=["%m/%d/%Y %I:%M %p"], required=False,  widget=forms.DateTimeInput(
		attrs={"class": "form-control m-input", "placeholder": "End", "autocomplete": "off"}))

	description = forms.CharField(widget=FroalaEditor(
		options={'toolbarInline': False, 'attribution': False, 'tableStyles': 'table'}))

	class Meta:
		model = Event
		fields = [
			"title", "url", "venue_name", "venue_address", "description", "start", "end", "image"
		]


		widgets = {

				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"My Awesome Event",
							"required": True,
							"maxlength": '100',
						}
					),

				"url": forms.TextInput(
						attrs={
							"class":"form-control m-input",
							"placeholder":"my-awesome-event",
							"onkeyup": "ValidateURL(this);"
						}
					),

				"venue_name": forms.TextInput(
						attrs={
							"class":"form-control m-input",
							"placeholder":"Venue",
						}
					),

				"venue_address": forms.TextInput(
						attrs={
							"autocomplete": "off",
							"class":"form-control m-input",
							"placeholder":"123 Main Street",
							"id":"autocomplete",
						}
					),

				"image": forms.FileInput(
						attrs={
							"onchange": "document.getElementById('image-placeholder').src = window.URL.createObjectURL(this.files[0])",
							"class":"form-control m-input dropzone",
						}
					),
			}



	def clean_image(self):
		image = self.cleaned_data.get('image')
		if image:
			image_extensions = ['.jpg', '.png', '.JPG', '.PNG', '.JPEG', '.jpeg']
			error = True
			for extension in image_extensions:
				if image.name.lower().endswith(extension) or image.name != self.instance.slug:
					error = False

			if error:
				raise forms.ValidationError('Only .jpg .png or .jpeg files are accepted.')
			return image
		else:
			return image


	def clean_end(self):
		start = self.cleaned_data.get('start')
		end = self.cleaned_data.get('end')

		if start and end:
			today = timezone.now()
			if start and end and start >= end:
				print("Did it even come here")		
				raise forms.ValidationError('The start date cannot be after the end date')
			elif end <= today:
				raise forms.ValidationError('Please change the end date of your event to be after today!')
			else:
				return end








