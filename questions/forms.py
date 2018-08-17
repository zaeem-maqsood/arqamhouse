from django import forms
from events.models import Event, EventGeneralQuestions, AttendeeGeneralQuestions
from .models import (EventQuestion, EventQuestionMultipleChoiceOption, AllTicketQuestionControl, TicketQuestion,
					AllTicketQuestionMultipleChoiceOption, TicketQuestionMultipleChoiceOption)



class EventGeneralQuestionsForm(forms.ModelForm):

	class Meta:
		model = EventGeneralQuestions
		fields = [
			"notes", "notes_required",
		]

		widgets = {

				"notes": forms.CheckboxInput(),
				"notes_required": forms.CheckboxInput(),
			}



class AttendeeGeneralQuestionsForm(forms.ModelForm):

	class Meta:
		model = AttendeeGeneralQuestions
		fields = [
			"name", "name_required", "gender", "email", "email_required"
		]

		widgets = {

				"name": forms.CheckboxInput(),
				"name_required": forms.CheckboxInput(),

				"gender": forms.CheckboxInput(),

				"email": forms.CheckboxInput(),
				"email_required": forms.CheckboxInput(),
			}




class TicketQuestionForm(forms.ModelForm):

	order = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={"class":"form-control m-input"}))

	class Meta:
		model = TicketQuestion
		fields = [
			"title", "required", "help_text", "order"
		]


		widgets = {

				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"Can I ask you a question?",
							"required": True,
							"maxlength": '100',
						}
					),

				"help_text": forms.TextInput(
						attrs={
							"class":"form-control m-input",
							"placeholder":"Please answer this question by doing so and so.",
						}
					),

				"required": forms.CheckboxInput(),
			}



class AllTicketQuestionForm(forms.ModelForm):

	order = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={"class":"form-control m-input"}))

	class Meta:
		model = AllTicketQuestionControl
		fields = [
			"title", "required", "help_text", "order"
		]


		widgets = {

				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"Can I ask you a question?",
							"required": True,
							"maxlength": '100',
						}
					),

				"help_text": forms.TextInput(
						attrs={
							"class":"form-control m-input",
							"placeholder":"Please answer this question by doing so and so.",
						}
					),

				"required": forms.CheckboxInput(),
			}



class EventQuestionBaseForm(forms.ModelForm):

	order = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={"class":"form-control m-input"}))

	class Meta:
		model = EventQuestion
		fields = [
			"title", "required", "help_text", "order"
		]


		widgets = {

				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"Can I ask you a question?",
							"required": True,
							"maxlength": '100',
						}
					),

				"help_text": forms.TextInput(
						attrs={
							"class":"form-control m-input",
							"placeholder":"Please answer this question by doing so and so.",
						}
					),

				"required": forms.CheckboxInput(),
			}


class EventQuestionMutipleChoiceOptionForm(forms.ModelForm):

	class Meta:
		model = EventQuestionMultipleChoiceOption
		fields = [
			"title",
		]


		widgets = {

				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"Option Title",
							"required": True,
							"maxlength": '100',
						}
					),
			}


class AllTicketQuestionMutipleChoiceOptionForm(forms.ModelForm):

	class Meta:
		model = AllTicketQuestionMultipleChoiceOption
		fields = [
			"title",
		]


		widgets = {

				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"Option Title",
							"required": True,
							"maxlength": '100',
						}
					),
			}


class TicketQuestionMutipleChoiceOptionForm(forms.ModelForm):

	class Meta:
		model = TicketQuestionMultipleChoiceOption
		fields = [
			"title",
		]


		widgets = {

				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"Option Title",
							"required": True,
							"maxlength": '100',
						}
					),
			}






