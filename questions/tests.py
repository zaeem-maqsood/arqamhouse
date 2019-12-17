from django.test import TestCase

from questions.models import Question, MultipleChoice
from houses.models import House


# Create your tests here.
class QuestionModelTestCase(TestCase):

    def setUp(self):
        house = House.objects.create(name="Arqam House")

    def test_unapproved_question(self):
        house = House.objects.get(name="Arqam House")
        question = Question.objects.create(house=house, title="Multiple Choice Question", question_type="Multiple Choice")
        self.assertEqual(question.approved, False)

    def test_approved_question(self):
        house = House.objects.get(name="Arqam House")
        question = Question.objects.create(house=house, title="Multiple Choice Question", question_type="Multiple Choice")
        multiple_choice = MultipleChoice.objects.create(question=question, title="Option A")
        multiple_choiceb = MultipleChoice.objects.create(question=question, title="Option B")
        question.save()
        question = Question.objects.get(title="Multiple Choice Question")
        self.assertEqual(question.approved, True)

