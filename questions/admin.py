from django.contrib import admin

from questions.models import Question, MultipleChoice

# Register your models here.
admin.site.register(Question)
admin.site.register(MultipleChoice)

