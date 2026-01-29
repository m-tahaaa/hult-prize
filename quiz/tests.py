from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from quiz.models import Question, Choice, QuizSettings, Leaderboard, Category

User = get_user_model()


class QuizTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.settings = QuizSettings.objects.create(
            quiz_title='Test Quiz',
            is_active=True,
            start_time=timezone.now() - timedelta(minutes=5),  # Started 5 mins ago
            end_time=timezone.now() + timedelta(hours=1),      # Ends in 1 hour
            default_duration=30,
            long_text_duration=45,
            short_text_duration=60,
        )
        
        # Create a test category (required for Question)
        self.category = Category.objects.create(
            category_name='General Knowledge'
        )
        
        # Create a test MCQ question
        self.question = Question.objects.create(
            question_text='What is 2 + 2?',
            question_type='mcq',
            category=self.category,
        )
        
        # Create choices
        self.correct_choice = Choice.objects.create(
            question=self.question,
            choice_text='4',
            is_correct=True
        )
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            choice_text='5',
            is_correct=False
        )
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_quiz_home_loads(self):
        """Test that quiz home page loads"""
        response = self.client.get('/quiz/')
        self.assertEqual(response.status_code, 200)

    def test_start_quiz_redirects(self):
        """Test that start quiz redirects to current question"""
        response = self.client.get('/quiz/start/')
        self.assertIn(response.status_code, [200, 302])

    def test_question_display(self):
        """Test that question displays correctly"""
        response = self.client.get(f'/quiz/question/{self.question.id}/')
        self.assertIn(response.status_code, [200, 302])

    def test_answer_submission(self):
        response = self.client.post(
            f'/quiz/question/{self.question.id}/',
            {'choice': self.correct_choice.id}
        )
        self.assertIn(response.status_code, [200, 302])

    def test_leaderboard(self):
        response = self.client.get('/quiz/leaderboard')
        self.assertEqual(response.status_code, 200)
