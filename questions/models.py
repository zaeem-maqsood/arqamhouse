import random
import string
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save
from django.urls import reverse

from events.models import Event
from events.models import Ticket


QUESTION_CHOICES = (
    (("Simple"), ("Simple")),
    (("Long"), ("Long")),
    (("Multiple Choice"), ("Multiple Choice")),
)

# Create your models here.
class Question(models.Model):

	title = models.CharField(max_length=100, null=True, blank=True)
	order = models.PositiveSmallIntegerField(blank=True, null=False, default=1)
	help_text = models.CharField(max_length=150, null=True, blank=True)
	required = models.BooleanField(default=False)
	question_type = models.CharField(max_length=50, blank=False, null=False, choices=QUESTION_CHOICES, default='simple')
	slug = models.SlugField(max_length = 375, unique = False, blank=True)
	deleted = models.BooleanField(default=False)
	approved = models.BooleanField(default=True)

	def __str__(self):
		return self.title



class MultipleChoice(models.Model):

	question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=False, null=False)
	title = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return self.title