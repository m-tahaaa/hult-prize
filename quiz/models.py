from django.db import models
import uuid
from django.contrib.auth.models import User

class BaseModel(models.Model): 
    uid = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract=True

class Category(BaseModel):
    category_name=models.CharField(max_length=100)
class Question(models.Model):
    TEXT = 'text'
    MCQ = 'mcq'
    CROSSWORD = 'crossword'

    QUESTION_TYPE_CHOICES = [
        (TEXT, 'Text Input'),
        (MCQ, 'Multiple Choice'),
        (CROSSWORD, 'Crossword')
    ]

    question_text = models.TextField()  # Instructions or question text
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES)
    correct_answer = models.TextField()  # Store the correct answer

    def __str__(self):
        return self.question_text


class Crossword(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='crossword')
    grid = models.TextField()  # Store the crossword grid in a serialized format (JSON)
    across_clues = models.TextField()  # JSON format for across clues
    down_clues = models.TextField()  # JSON format for down clues

    def __str__(self):
        return f"Crossword for Question: {self.question.id}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)  # Flag to indicate the correct answer

    def __str__(self):
        return self.choice_text


class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)  # For text input questions
    selected_choice = models.ForeignKey(Choice, blank=True, null=True, on_delete=models.CASCADE)  # For MCQ
    crossword_solution = models.TextField(blank=True, null=True)  # Store crossword answers

    def __str__(self):
        return f'{self.user} - {self.question}'


class Leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Each user has one entry in the leaderboard
    points = models.IntegerField(default=0)  # Default points set to 0

    def __str__(self):
        return f'{self.user.username}: {self.points} points'
