from django import forms

from .models import Attendee
from answers.models import TicketAnswer
from questions.models import TicketQuestion
from core.constants import genders


class AttendeeForm(forms.ModelForm):

	class Meta:
		model = Attendee
		fields = [
			"name", "email", "gender",
		]


		widgets = {

				"name": forms.TextInput(
						attrs={
							"class":"form-control m-input",
							"placeholder":"Full Name",
							"required": True,
						}
					),

				"email": forms.EmailInput(
						attrs={
							"class":"form-control m-input",
							"placeholder":"someone@example.com",
						}
					),

				"gender": forms.Select(
						attrs={
							"class":"form-control m-input",
							"required": True,
						}
					),
			}




	def __init__(self, event, *args, **kwargs):
		
		questions = TicketQuestion.objects.filter(event=event)

		super(AttendeeForm, self).__init__(*args, **kwargs)
		for question in questions:
			if question.simple_question:
				self.fields["%s_question" % (question.id)] = forms.CharField(label=str(question.title), widget=forms.TextInput(attrs={"class":"form-control m-input"}), required=question.required)
			elif question.paragraph_question:
				self.fields["%s_question" % (question.id)] = forms.CharField(label=str(question.title), widget=forms.Textarea(attrs={"class":"form-control m-input", "rows": "4"}), required=question.required)
			elif question.multiple_choice_question:
				options = EventQuestionMultipleChoiceOption.objects.filter(event_question=question, deleted=False)
				choices_for_question = []
				for option in options:
					sub_list = []
					sub_list.append(option.title)
					sub_list.append(option.title)
					choices_for_question.append(sub_list)
				self.fields["%s_question" % (question.id)] = forms.ChoiceField(label=str(question.title), widget=forms.Select(attrs={"class":"form-control m-input"}), required=question.required, choices=choices_for_question)


		


















