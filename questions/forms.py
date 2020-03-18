from django import forms
from events.models import Event, AttendeeCommonQuestions
from questions.models import Question, MultipleChoice




class MutipleChoiceForm(forms.ModelForm):

	class Meta:
		model = MultipleChoice
		fields = [
			"title",
		]


		widgets = {

				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder":"Option A",
							"required": True,
							"maxlength": '100',
						}
					),
			}



class QuestionForm(forms.ModelForm):


	class Meta:
		model = Question
		fields = [
			"title", "required", "help_text", "question_type",
		]


		widgets = {

				"title": forms.TextInput(
						attrs={
							"class":"form-control m-input message",
							"placeholder": "What's your favorite color?",
							"required": True,
							"maxlength": '100',
						}
					),

				"help_text": forms.Textarea(
						attrs={
							"class":"form-control m-input",
							"placeholder":"Enter some 'help text' here to help your ticket buyers answer this question.",
							"rows" : 2,
						}
					),

				"required": forms.CheckboxInput(),

				"question_type": forms.Select(
						attrs={
							"required" : True,
							"class":"form-control m-input",
						}
					),
			}
