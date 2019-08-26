
from .base import *

from events.views import QuestionsListView

urlpatterns += [
    path('<slug:slug>/questions', QuestionsListView.as_view(), name='list_questions'),
]