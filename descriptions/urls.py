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

from .views import (H1TitleCreateView, H1TitleUpdateView, H2TitleCreateView, H2TitleUpdateView,
					H3TitleCreateView, H3TitleUpdateView, ParagraphCreateView, ParagraphUpdateView)

app_name = "descriptions"

urlpatterns = [

    path('h1title/create/<slug:slug>/<int:type_id>', H1TitleCreateView.as_view(), name='h1title_create'),
    path('h1title/update/<slug:slug>/<int:type_id>/<int:h1_title_id>', H1TitleUpdateView.as_view(), name='h1title_update'),


    path('h2title/create/<slug:slug>/<int:type_id>', H2TitleCreateView.as_view(), name='h2title_create'),
    path('h2title/update/<slug:slug>/<int:type_id>/<int:h2_title_id>', H2TitleUpdateView.as_view(), name='h2title_update'),


    path('h3title/create/<slug:slug>/<int:type_id>', H3TitleCreateView.as_view(), name='h3title_create'),
    path('h3title/update/<slug:slug>/<int:type_id>/<int:h3_title_id>', H3TitleUpdateView.as_view(), name='h3title_update'),


    path('paragraph/create/<slug:slug>/<int:type_id>', ParagraphCreateView.as_view(), name='paragraph_create'),
    path('paragraph/update/<slug:slug>/<int:type_id>/<int:paragraph_id>', ParagraphUpdateView.as_view(), name='paragraph_update'),

]