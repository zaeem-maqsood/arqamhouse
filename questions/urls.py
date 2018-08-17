"""Arqam House Events URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import (EventQuestionCreateView, QuestionsListView, EventQuestionUpdateView, 
                    EventQuestionMultipleChoiceOptionCreateView, EventQuestionMultipleChoiceOptionUpdateView,
                    AllTicketQuestionCreateView, AllTicketQuestionUpdateView, TicketQuestionCreateView,
                    TicketQuestionUpdateView, AllTicketQuestionMultipleChoiceOptionCreateView,
                    AllTicketQuestionMultipleChoiceOptionUpdateView, TicketQuestionMultipleChoiceOptionCreateView,
                    TicketQuestionMultipleChoiceOptionUpdateView)

app_name="questions"

urlpatterns = [

    path('', QuestionsListView.as_view(), name='list_questions'),

    # Event Questions
    path('event-create/simple', EventQuestionCreateView.as_view(), name='create_simple', kwargs={"type":"simple"}),
    path('event-create/paragraph', EventQuestionCreateView.as_view(), name='create_paragraph', kwargs={"type":"paragraph"}),
    path('event-create/multiple-choice', EventQuestionCreateView.as_view(), name='create_multiple_choice', kwargs={"type":"multiple choice"}),
    
    path('update/<slug:question_slug>', EventQuestionUpdateView.as_view(), name='update_event_question'),

    path('event-create/multiple-choice/<slug:question_slug>/add-option', EventQuestionMultipleChoiceOptionCreateView.as_view(), name='create_multiple_choice_option'),
    path('event-create/multiple-choice/<slug:question_slug>/update-option/<slug:option_slug>', EventQuestionMultipleChoiceOptionUpdateView.as_view(), name='update_multiple_choice_option'),
    

    # All Ticket Question
    path('all-ticket-create/simple', AllTicketQuestionCreateView.as_view(), name='all_ticket_create_simple', kwargs={"type":"simple"}),
    path('all-ticket-create/paragraph', AllTicketQuestionCreateView.as_view(), name='all_ticket_create_paragraph', kwargs={"type":"paragraph"}),
    path('all-ticket-create/multiple-choice', AllTicketQuestionCreateView.as_view(), name='all_ticket_create_multiple_choice', kwargs={"type":"multiple choice"}),

    path('update-all-ticket/<slug:question_slug>', AllTicketQuestionUpdateView.as_view(), name='update_all_ticket_question'),

    path('all-ticket-create/multiple-choice/<slug:question_slug>/add-option', AllTicketQuestionMultipleChoiceOptionCreateView.as_view(), name='create_all_ticket_multiple_choice_option'),
    path('all-ticket-create/multiple-choice/<slug:question_slug>/update-option/<slug:option_slug>', AllTicketQuestionMultipleChoiceOptionUpdateView.as_view(), name='update_all_ticket_multiple_choice_option'),



    # Single Ticket Questions
    path('ticket-create/simple/<slug:ticket_slug>', TicketQuestionCreateView.as_view(), name='ticket_create_simple', kwargs={"type":"simple"}),
    path('ticket-create/paragraph/<slug:ticket_slug>', TicketQuestionCreateView.as_view(), name='ticket_create_paragraph', kwargs={"type":"paragraph"}),
    path('ticket-create/multiple-choice/<slug:ticket_slug>', TicketQuestionCreateView.as_view(), name='ticket_create_multiple_choice', kwargs={"type":"multiple choice"}),

    path('update-ticket/<slug:ticket_slug>/<slug:question_slug>', TicketQuestionUpdateView.as_view(), name='update_ticket_question'),

    path('ticket-create/multiple-choice/<slug:question_slug>/add-option/<slug:ticket_slug>', TicketQuestionMultipleChoiceOptionCreateView.as_view(), name='create_ticket_multiple_choice_option'),
    path('ticket-create/multiple-choice/<slug:question_slug>/update-option/<slug:ticket_slug>/<slug:option_slug>', TicketQuestionMultipleChoiceOptionUpdateView.as_view(), name='update_ticket_multiple_choice_option'),

]










