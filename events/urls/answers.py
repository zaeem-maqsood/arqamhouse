from .base import *
from events.views import AnswersView, AnswerDetailView, AnalyticAnswersView

urlpatterns += [

    path('<slug:slug>/answers/', AnswersView.as_view(), name='answers_list'),
    path('<slug:slug>/answers/analytic',
         AnalyticAnswersView.as_view(), name='answers_list_analytic'),
    path('<slug:slug>/answers/<int:event_question_id>/', AnswerDetailView.as_view(), name='answer_detail'),

]
