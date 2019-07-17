from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.http import Http404, HttpResponseRedirect, HttpResponse



from houses.mixins import HouseAccountMixin

from .forms import (H1TitleForm, H2TitleForm, H3TitleForm, ParagraphForm)
from .models import (EventDescription, H1Title, H2Title, H3Title, Paragraph)
from events.models import Event



# Create your views here.





# -------------------------------------------------------------- Paragraph Description Element ----------------------------
class ParagraphCreateView(HouseAccountMixin, CreateView):
	model = Paragraph
	form_class = ParagraphForm
	template_name = "descriptions/paragraph_form.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get_success_url(self):

		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Define Types Here
		if type_id == 0:
			view_name = "events:description"

		return reverse(view_name, kwargs={"slug": slug})

	def get_context_data(self, form, *args, **kwargs):
		context = {}
		
		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Define Types Here 
		if type_id == 0:
			entity_type = "event"

		context["entity_type"] = entity_type
		context["slug"] = slug
		context["form"] = form
		return context

	def get(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form))

	def post(self, request, *args, **kwargs):
		data = request.POST
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, request):
		data = request.POST
		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Based off of the type get object and description models
		if type_id == 0:
			event = self.get_event(slug)
			event_description = EventDescription.objects.get(event=event)
			form.instance.description = event_description
		
		self.object = form.save()
		self.object.save()
		messages.success(request, 'Paragraph Element Created')
		valid_data = super(ParagraphCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))


class ParagraphUpdateView(HouseAccountMixin, CreateView):
	model = Paragraph
	form_class = ParagraphForm
	template_name = "descriptions/paragraph_form.html"

	def get_success_url(self):
		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Return based off of type
		if type_id == 0:
			view_name = "events:description"

		return reverse(view_name, kwargs={"slug": slug})

	def get_context_data(self, form, *args, **kwargs):
		context = {}

		slug = self.kwargs['slug']
		paragraph_id = self.kwargs['paragraph_id']
		type_id = self.kwargs['type_id']

		if type_id == 0:
			entity_type = "event"

		context["entity_type"] = entity_type
		context["slug"] = slug
		context["form"] = form
		context["update"] = True
		return context

	def get(self, request, *args, **kwargs):
		paragraph_id = self.kwargs['paragraph_id']
		self.object = Paragraph.objects.get(id=paragraph_id)
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form))

	def post(self, request, *args, **kwargs):
		data = request.POST

		paragraph_id = self.kwargs['paragraph_id']
		self.object = Paragraph.objects.get(id=paragraph_id)
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, request):
		data = request.POST

		if "Delete Element" in data:
			self.object.delete()
			messages.warning(request, 'Element Deleted Successfully')
			return HttpResponseRedirect(self.get_success_url())

		self.object = form.save()
		messages.success(request, 'Paragraph Updated')
		valid_data = super(ParagraphUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))

# -------------------------------------------------------------- Paragraph Description Element ----------------------------













# -------------------------------------------------------------- H3 Title Description Element ----------------------------
class H3TitleCreateView(HouseAccountMixin, CreateView):
	model = H3Title
	form_class = H3TitleForm
	template_name = "descriptions/h3_title_form.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get_success_url(self):

		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Define Types Here
		if type_id == 0:
			view_name = "events:description"

		return reverse(view_name, kwargs={"slug": slug})

	def get_context_data(self, form, *args, **kwargs):
		context = {}
		
		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Define Types Here 
		if type_id == 0:
			entity_type = "event"

		context["entity_type"] = entity_type
		context["slug"] = slug
		context["form"] = form
		return context

	def get(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form))

	def post(self, request, *args, **kwargs):
		data = request.POST
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, request):
		data = request.POST
		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Based off of the type get object and description models
		if type_id == 0:
			event = self.get_event(slug)
			event_description = EventDescription.objects.get(event=event)
			form.instance.description = event_description
		
		self.object = form.save()
		self.object.save()
		messages.success(request, 'H3 Title Created')
		valid_data = super(H3TitleCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))


class H3TitleUpdateView(HouseAccountMixin, CreateView):
	model = H3Title
	form_class = H3TitleForm
	template_name = "descriptions/h3_title_form.html"

	def get_success_url(self):
		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Return based off of type
		if type_id == 0:
			view_name = "events:description"

		return reverse(view_name, kwargs={"slug": slug})

	def get_context_data(self, form, *args, **kwargs):
		context = {}

		slug = self.kwargs['slug']
		h3_title_id = self.kwargs['h3_title_id']
		type_id = self.kwargs['type_id']

		if type_id == 0:
			entity_type = "event"

		context["entity_type"] = entity_type
		context["slug"] = slug
		context["form"] = form
		context["update"] = True
		return context

	def get(self, request, *args, **kwargs):
		h3_title_id = self.kwargs['h3_title_id']
		self.object = H3Title.objects.get(id=h3_title_id)
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form))

	def post(self, request, *args, **kwargs):
		data = request.POST

		h3_title_id = self.kwargs['h3_title_id']
		self.object = H3Title.objects.get(id=h3_title_id)
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, request):
		data = request.POST

		if "Delete Element" in data:
			self.object.delete()
			messages.warning(request, 'Element Deleted Successfully')
			return HttpResponseRedirect(self.get_success_url())

		self.object = form.save()
		messages.success(request, 'H3 Title Updated')
		valid_data = super(H3TitleUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))

# -------------------------------------------------------------- H3 Title Description Element ----------------------------











# -------------------------------------------------------------- H2 Title Description Element ----------------------------
class H2TitleCreateView(HouseAccountMixin, CreateView):
	model = H2Title
	form_class = H2TitleForm
	template_name = "descriptions/h2_title_form.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get_success_url(self):

		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Define Types Here
		if type_id == 0:
			view_name = "events:description"

		return reverse(view_name, kwargs={"slug": slug})

	def get_context_data(self, form, *args, **kwargs):
		context = {}
		
		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Define Types Here 
		if type_id == 0:
			entity_type = "event"

		context["entity_type"] = entity_type
		context["slug"] = slug
		context["form"] = form
		return context

	def get(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form))

	def post(self, request, *args, **kwargs):
		data = request.POST
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, request):
		data = request.POST
		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Based off of the type get object and description models
		if type_id == 0:
			event = self.get_event(slug)
			event_description = EventDescription.objects.get(event=event)
			form.instance.description = event_description
		
		self.object = form.save()
		self.object.save()
		messages.success(request, 'H2 Title Created')
		valid_data = super(H2TitleCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))


class H2TitleUpdateView(HouseAccountMixin, CreateView):
	model = H2Title
	form_class = H2TitleForm
	template_name = "descriptions/h2_title_form.html"

	def get_success_url(self):
		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Return based off of type
		if type_id == 0:
			view_name = "events:description"

		return reverse(view_name, kwargs={"slug": slug})

	def get_context_data(self, form, *args, **kwargs):
		context = {}

		slug = self.kwargs['slug']
		h2_title_id = self.kwargs['h2_title_id']
		type_id = self.kwargs['type_id']

		if type_id == 0:
			entity_type = "event"

		context["entity_type"] = entity_type
		context["slug"] = slug
		context["form"] = form
		context["update"] = True
		return context

	def get(self, request, *args, **kwargs):
		h2_title_id = self.kwargs['h2_title_id']
		self.object = H2Title.objects.get(id=h2_title_id)
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form))

	def post(self, request, *args, **kwargs):
		data = request.POST

		h2_title_id = self.kwargs['h2_title_id']
		self.object = H2Title.objects.get(id=h2_title_id)
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, request):
		data = request.POST

		if "Delete Element" in data:
			self.object.delete()
			messages.warning(request, 'Element Deleted Successfully')
			return HttpResponseRedirect(self.get_success_url())

		self.object = form.save()
		messages.success(request, 'H2 Title Updated')
		valid_data = super(H2TitleUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))

# -------------------------------------------------------------- H2 Title Description Element ----------------------------











# -------------------------------------------------------------- H1 Title Description Element ----------------------------
class H1TitleCreateView(HouseAccountMixin, CreateView):
	model = H1Title
	form_class = H1TitleForm
	template_name = "descriptions/h1_title_form.html"

	def get_event(self, slug):
		try:
			event = Event.objects.get(slug=slug)
			return event
		except Exception as e:
			print(e)
			raise Http404

	def get_success_url(self):

		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Define Types Here
		if type_id == 0:
			view_name = "events:description"

		return reverse(view_name, kwargs={"slug": slug})

	def get_context_data(self, form, *args, **kwargs):
		context = {}
		
		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Define Types Here 
		if type_id == 0:
			entity_type = "event"

		context["entity_type"] = entity_type
		context["slug"] = slug
		context["form"] = form
		return context

	def get(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form))

	def post(self, request, *args, **kwargs):
		data = request.POST
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, request):
		data = request.POST
		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Based off of the type get object and description models
		if type_id == 0:
			event = self.get_event(slug)
			event_description = EventDescription.objects.get(event=event)
			form.instance.description = event_description
		
		self.object = form.save()
		self.object.save()
		messages.success(request, 'H1 Title Created')
		valid_data = super(H1TitleCreateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))


class H1TitleUpdateView(HouseAccountMixin, CreateView):
	model = H1Title
	form_class = H1TitleForm
	template_name = "descriptions/h1_title_form.html"

	def get_success_url(self):
		slug = self.kwargs['slug']
		type_id = self.kwargs['type_id']

		# Return based off of type
		if type_id == 0:
			view_name = "events:description"

		return reverse(view_name, kwargs={"slug": slug})

	def get_context_data(self, form, *args, **kwargs):
		context = {}

		slug = self.kwargs['slug']
		h1_title_id = self.kwargs['h1_title_id']
		type_id = self.kwargs['type_id']

		if type_id == 0:
			entity_type = "event"

		context["entity_type"] = entity_type
		context["slug"] = slug
		context["form"] = form
		context["update"] = True
		return context

	def get(self, request, *args, **kwargs):
		h1_title_id = self.kwargs['h1_title_id']
		self.object = H1Title.objects.get(id=h1_title_id)
		form = self.get_form()
		return self.render_to_response(self.get_context_data(form=form))

	def post(self, request, *args, **kwargs):
		data = request.POST

		h1_title_id = self.kwargs['h1_title_id']
		self.object = H1Title.objects.get(id=h1_title_id)
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form, request)
		else:
			return self.form_invalid(form)

	def form_valid(self, form, request):
		data = request.POST

		if "Delete Element" in data:
			self.object.delete()
			messages.warning(request, 'Element Deleted Successfully')
			return HttpResponseRedirect(self.get_success_url())

		self.object = form.save()
		messages.success(request, 'H1 Title Updated')
		valid_data = super(H1TitleUpdateView, self).form_valid(form)
		return valid_data

	def form_invalid(self, form):
		print(form.errors)
		return self.render_to_response(self.get_context_data(form=form))

# -------------------------------------------------------------- H1 Title Description Element ----------------------------









































