from django.contrib import admin


from .models import EventQuestion, AllTicketQuestionControl, TicketQuestion, EventQuestionMultipleChoiceOption

# Register your models here.
admin.site.register(EventQuestion)
admin.site.register(EventQuestionMultipleChoiceOption)
admin.site.register(AllTicketQuestionControl)
admin.site.register(TicketQuestion)

