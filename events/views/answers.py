from .base import *
from events.models import (AttendeeCommonQuestions, EventQuestion, OrderAnswer, Answer, Attendee, EventOrder)


class AnalyticAnswersView(HouseAccountMixin, View):

	template_name = "events/answers/analytic_answer_details.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())

	def post(self, request, *args, **kwargs):
		data = request.POST
		print(data)

		if 'attendees' in data:

			event = self.get_event(self.kwargs['slug'])
			all_attendees = Attendee.objects.filter(
				order__event=event, active=True).order_by('created_at')
			search_terms = data["search"].split()

			if data["search"] == '':
				attendees = all_attendees
			else:
				counter = 0
				for search_term in search_terms:
					if counter == 0:
						attendees = all_attendees.filter(
							Q(name__icontains=search_term) | Q(age__icontains=search_term) | Q(city__name__icontains=search_term) | Q(gender__icontains=search_term))
					else:
						attendees = attendees.filter(Q(name__icontains=search_term) | Q(age__icontains=search_term) | Q(
							city__name__icontains=search_term) | Q(gender__icontains=search_term))
					print(counter)
					counter += 1

			attendees = attendees[:100]
			print(attendees)
			html = render_to_string(
				'events/answers/analytic_answer_dynamic_table_body.html', {'attendees': attendees, 'request': request})
			return HttpResponse(html)

	def get_context_data(self, *args, **kwargs):
		context = {}
		house = self.get_house()
		event = self.get_event(self.kwargs['slug'])
		attendees = Attendee.objects.filter(order__event=event, active=True)

		context["attendees"] = attendees
		context["house"] = house
		context["event"] = event
		context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context


class AnswerDetailView(HouseAccountMixin, View):

	template_name = "events/answers/answer_details.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get_event_question(self, event_question_id):
		try:
			event_question = EventQuestion.objects.get(pk=event_question_id)
			return event_question
		except Exception as e:
			print(e)
			raise Http404

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())

	def post(self, request, *args, **kwargs):
		data = request.POST
		print(data)

		if 'attendees' in data:

			event = self.get_event(self.kwargs['slug'])
			all_attendees = Attendee.objects.filter(order__event=event, active=True).order_by('created_at')
			search_terms = data["search"].split()

			if data["search"] == '':
				attendees = all_attendees
			else:
				counter = 0
				for search_term in search_terms:
					if counter == 0:
						attendees = all_attendees.filter(Q(name__icontains=search_term))
					else:
						attendees = attendees.filter(Q(name__icontains=search_term))
					print(counter)
					counter += 1

			attendees = attendees[:100]
			print(attendees)
			html = render_to_string(
				'events/answers/answer-dynamic-table-body.html', {'attendees': attendees, 'request': request})
			return HttpResponse(html)

		if 'orders' in data:
			event = self.get_event(self.kwargs['slug'])
			all_orders = EventOrder.objects.filter(
				event=event, failed=False, refunded=False).order_by('created_at')
			search_terms = data["search"].split()

			if data["search"] == '':
				orders = all_orders
			else:
				counter = 0
				for search_term in search_terms:
					if counter == 0:
						orders = all_orders.filter(Q(name__icontains=search_term))
					else:
						orders = orders.filter(Q(name__icontains=search_term))
					print(counter)
					counter += 1

			orders = orders[:100]
			print(orders)
			html = render_to_string(
				'events/answers/order-dynamic-table-body.html', {'orders': orders, 'request': request})
			return HttpResponse(html)

	def get_context_data(self, *args, **kwargs):
		context = {}
		house = self.get_house()
		event = self.get_event(self.kwargs['slug'])
		event_question = self.get_event_question(self.kwargs['event_question_id'])
		attendees = Attendee.objects.filter(order__event=event, active=True)
		orders = EventOrder.objects.filter(event=event, failed=False, refunded=False)

		context["orders"] = orders
		context["attendees"] = attendees
		context["event_question"] = event_question
		context["house"] = house
		context["event"] = event
		context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context



class AnswersView(HouseAccountMixin, View):
	
	template_name = "events/answers/list_answers.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get_ages(self, attendees):
		ages = []
		under_12 = 0
		twelve_to_17 = 0
		eighteen_to_24 = 0
		twentyfive_to_34 = 0
		thirtyfive_to_44 = 0
		fourtyfive_to_54 = 0
		fiftyfive_to_64 = 0
		sixtyfive_to_74 = 0
		over_75 = 0
		no_data = 0
		for attendee in attendees:
			age = attendee.age
			if age:
				if age < 12:
					under_12 += 1
				elif age >= 12 and age <= 17:
					twelve_to_17 += 1
				elif age >= 18 and age <= 24:
					eighteen_to_24 += 1
				elif age >= 25 and age <= 44:
					twentyfive_to_34 += 1
				elif age >= 35 and age <= 44:
					thirtyfive_to_44 += 1
				elif age >= 45 and age <= 54:
					fourtyfive_to_54 += 1
				elif age >= 55 and age <= 64:
					fiftyfive_to_64 += 1
				elif age >= 65 and age <= 74:
					sixtyfive_to_74 += 1
				else:
					over_75 += 1
			else:
				no_data += 1
		ages.append(under_12)
		ages.append(twelve_to_17)
		ages.append(eighteen_to_24)
		ages.append(twentyfive_to_34)
		ages.append(thirtyfive_to_44)
		ages.append(fourtyfive_to_54)
		ages.append(fiftyfive_to_64)
		ages.append(sixtyfive_to_74)
		ages.append(over_75)
		ages.append(no_data)
		return ages

	def get_genders(self, attendees):
		genders = []
		male = 0
		female = 0
		no_data = 0
		for attendee in attendees:
			gender = attendee.gender
			if gender:
				if gender == 'male':
					male += 1
				else:
					female += 1
			else:
				no_data += 1
		genders.append(male)
		genders.append(female)
		genders.append(no_data)
		return genders
					


	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())


	def get_context_data(self, *args, **kwargs):
		context = {}
		house = self.get_house()
		event = self.get_event(self.kwargs['slug'])
		
		attendee_common_question = AttendeeCommonQuestions.objects.get(event=event)
		event_questions = EventQuestion.objects.filter(event=event, question__deleted=False)
		context["event_questions"] = event_questions
		context["attendee_common_question"] = attendee_common_question

		if attendee_common_question.age or attendee_common_question.gender or attendee_common_question.address:
			attendees = Attendee.objects.filter(order__event=event, active=True).order_by('age')
			context["attendees"] = attendees
			if attendee_common_question.age:
				ages = self.get_ages(attendees)
				context["ages"] = ages
			if attendee_common_question.gender:
				genders = self.get_genders(attendees)
				context["genders"] = genders

		context["house"] = house
		context["event"] = event
		context["event_tab"] = True
		context["dashboard_events"] = self.get_events()
		return context
