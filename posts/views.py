import json
from django.db.models import Q
from django.core import serializers
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.list import ListView
from django.views import View
from django.urls import reverse
from django.conf import settings

from django.core.mail import send_mail, EmailMultiAlternatives

from weasyprint import HTML, CSS
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string

from itertools import chain
from operator import attrgetter

from houses.mixins import HouseAccountMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from events.mixins import EventSecurityMixin
from django.contrib import messages

from posts.models import Post
from posts.forms import PostForm

from donations.models import Donation
from houses.models import House
from profiles.models import Profile
from django.contrib.auth.models import User
from events.models import EventOrder, Attendee, Event, Ticket, EventCart, EventCartItem



# Create your views here.
class EditPostView(HouseAccountMixin, FormView):
    template_name = "posts/edit_post.html"

    def get_success_url(self):
        view_name = "edit_post"
        return reverse(view_name, kwargs={"slug": self.kwargs['slug'], "post_number": self.kwargs["post_number"]})

    def get(self, request, *args, **kwargs):
        self.object = None
        house = self.get_house()
        post = self.get_post(house)
        form = PostForm(house=house, instance=post)
        return self.render_to_response(self.get_context_data(form=form, request=request))


    def get_post(self, house):
        post_number = self.kwargs['post_number']
        try:
            post = Post.objects.get(post_number=int(post_number), house=house)
            return post
        except Exception as e:
            print(e)
            raise Http404


    def get_context_data(self, form, request, *args, **kwargs):
        context = {}
        house = self.get_house()
        post = self.get_post(house)
        context["house"] = house
        context["form"] = form
        return context


    def post(self, request, *args, **kwargs):
        data = request.POST
        house = self.get_house()
        post = self.get_post(house)

        form = PostForm(data=data, house=house, instance=post)
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form, request)


    def form_valid(self, form, request):
        data = request.POST
        house = self.get_house()

        json_data = json.loads(request.body)
        print(json_data)
        print("it came to the post")
        if json_data:
            content = json_data['editor_html']
            self.object.content = content
        else:
            self.object = form.save(commit=False)

        self.object.save()
        messages.success(request, 'Post Created Successfully!')
        valid_data = super(EditPostView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form, request):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form, request=request))
