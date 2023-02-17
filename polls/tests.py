import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for old questions.
        """
        time = timezone.now() - datetime.timedelta(days=3)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions within 24 hours.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertTrue(recent_question.was_published_recently())

class QuestionViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        r = self.client.get(reverse('polls:index'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'No polls are available.')
        self.assertQuerysetEqual(r.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        q = create_question(question_text='Past question.', days=-30)
        r = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(r.context['latest_question_list'], [q])

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on the index page.
        """
        q = create_question(question_text='Future question.', days=30)
        r = self.client.get(reverse('polls:index'))
        self.assertContains(r, 'No polls are available.')
        self.assertQuerysetEqual(r.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        When there is a future and past question, only past question is displayed.
        """
        pq = create_question(question_text='Past question.', days=-30)
        create_question(question_text='Future question.', days=30)
        r = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(r.context['latest_question_list'], [pq])

    def test_two_past_questions(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        q1 = create_question(question_text='Past question 1.', days=-30)
        q2 = create_question(question_text='Past question 2.', days=-5)
        r = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(r.context['latest_question_list'], [q2, q1])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        Detail for future question should 404.
        """
        fq = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(fq.id,))
        r = self.client.get(url)
        self.assertEqual(r.status_code, 404)

    def test_past_question(self):
        """
        Detail for past question should display question text.
        """
        pq = create_question(question_text='Future question.', days=-5)
        url = reverse('polls:detail', args=(pq.id,))
        r = self.client.get(url)
        self.assertContains(r, pq.question_text)