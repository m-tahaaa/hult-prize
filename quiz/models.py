from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils.timezone import now
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(BaseModel):
    category_name = models.CharField(max_length=255)
    def __str__(self) -> str:
        return self.category_name
    
class Question(BaseModel):

    TEXT = 'text'
    MCQ = 'mcq'

    QUESTION_TYPE_CHOICES = [
        (TEXT, 'Text Input'),
        (MCQ, 'Multiple Choice'),
    ]
    
    category=models.ForeignKey(Category, related_name='category',on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES)
    marks = models.IntegerField(default=10)
    correct_answer = models.TextField(blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.question_text

class Choice(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.choice_text


class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    selected_choice = models.ForeignKey(Choice, blank=True, null=True, on_delete=models.CASCADE)
    submission_time = models.DateTimeField(default=now)  

    def __str__(self):
        return f'{self.user} - {self.question}'

class Leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username}: {self.points} points'


class QuizSettings(models.Model):
    quiz_title = models.CharField(max_length=255, default="Quiz")
    start_time = models.DateTimeField(help_text="When the quiz starts (all users see Q1)")
    end_time = models.DateTimeField(help_text="When the quiz ends completely")
    default_duration = models.IntegerField(default=30, help_text="Default seconds per MCQ question")
    short_text_duration = models.IntegerField(default=50, help_text="Seconds for fill-in-the-blank questions")
    long_text_duration = models.IntegerField(default=150, help_text="Seconds for long passage questions")
    long_text_threshold = models.IntegerField(default=150, help_text="Character count to consider a question 'long'")
    is_active = models.BooleanField(default=False, help_text="Enable/disable the quiz")

    class Meta:
        verbose_name = "Quiz Settings"
        verbose_name_plural = "Quiz Settings"

    def __str__(self):
        return f"{self.quiz_title} - {'Active' if self.is_active else 'Inactive'}"

    def save(self, *args, **kwargs):
        # Ensure only one QuizSettings instance exists
        if not self.pk and QuizSettings.objects.exists():
            raise ValueError("Only one QuizSettings instance is allowed")
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get the quiz settings, create default if none exists"""
        settings = cls.objects.first()
        if not settings:
            from django.utils import timezone
            settings = cls.objects.create(
                start_time=timezone.now(),
                end_time=timezone.now(),
                is_active=False
            )
        return settings
