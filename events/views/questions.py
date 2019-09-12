from .base import *

from events.models import Event, EventQuestion, AttendeeCommonQuestions
from houses.mixins import HouseAccountMixin


class QuestionsListView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, View):

	template_name = "events/questions/list_questions.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
		except Exception as e:
			print(e)
			raise Http404
		return event


	def post(self, request, *args, **kwargs):
		data = request.POST
		print(data)

		event = self.get_event(self.kwargs['slug'])
		attendee_common_questions = AttendeeCommonQuestions.objects.get(event=event)

		option = data['option']
		value = data['value']
		required = data['required']

		if value == "true":
			value = True
		else:
			value = False


		if required == 'true':
			required = True
		else:
			required = False


		if option == 'id_notes':
			print(value)
			attendee_common_questions.notes = value
			attendee_common_questions.notes_required = required
			attendee_common_questions.save()

		if option == 'id_age':
			attendee_common_questions.age = value
			attendee_common_questions.age_required = required
			attendee_common_questions.save()

		if option == 'id_gender':
			attendee_common_questions.gender = value
			attendee_common_questions.gender_required = required
			attendee_common_questions.save()

			
		return render(request, self.template_name, self.get_context_data())


	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())


	def get_context_data(self, *args, **kwargs):
		context = {}

		house = self.get_house()
		context["house"] = house
		
		event = self.get_event(self.kwargs['slug'])
		context["event"] = event


		event_questions = EventQuestion.objects.filter(event=event, question__deleted=False).order_by("question__order")
		context["event_questions"] = event_questions

		attendee_common_questions = AttendeeCommonQuestions.objects.get(event=event)
		context["attendee_common_questions"] = attendee_common_questions
	

		context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context

