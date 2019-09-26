import random
import string
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save
from django.urls import reverse

from events.models import Event, Ticket
from houses.models import House


QUESTION_CHOICES = (
    (("Simple"), ("Simple")),
    (("Long"), ("Long")),
    (("Multiple Choice"), ("Multiple Choice")),
)

# Create your models here.
class Question(models.Model):

	house = models.ForeignKey(House, on_delete=models.CASCADE, blank=True, null=True)
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

	def _approve(self):
		
		if self.question_type == 'Multiple Choice':
			multiple_choice = MultipleChoice.objects.filter(question=self, deleted=False)
			if not multiple_choice.count() > 1:
				self.approved = False
			else:
				self.approved = True

	def save(self, *args, **kwargs):
		self._approve()

		super().save(*args, **kwargs)



class MultipleChoice(models.Model):

	question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=False, null=False)
	title = models.CharField(max_length=100, null=True, blank=True)
	deleted = models.BooleanField(default=False)

	def __str__(self):
		return self.title
