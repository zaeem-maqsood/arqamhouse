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

from questions.views import QuestionCreateView, QuestionUpdateView, MultipleChoiceCreateView, MultipleChoiceUpdateView

app_name="questions"

urlpatterns = [

    path('<one_to_one_type>/<int:one_to_one_id>/create/', QuestionCreateView.as_view(), name='create_question'),
    path('<one_to_one_type>/<int:one_to_one_id>/update/<int:pk>', QuestionUpdateView.as_view(), name='update_question'),
    path('<one_to_one_type>/<int:one_to_one_id>/update/<int:pk>/option/create', MultipleChoiceCreateView.as_view(), name='create_option'),
    path('<one_to_one_type>/<int:one_to_one_id>/update/<int:pk>/option/update/<int:option_id>', MultipleChoiceUpdateView.as_view(), name='update_option')
]










