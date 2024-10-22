from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()

    def __str__(self):
        return self.title


class Question(models.Model):
    TEXT = 'text'
    MCQ = 'mcq'
    CROSSWORD = 'crossword'  # New question type for crosswords

    QUESTION_TYPE_CHOICES = [
        (TEXT, 'Text Input'),
        (MCQ, 'Multiple Choice'),
        (CROSSWORD, 'Crossword')  # Adding crossword as a choice
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()  # Can be used for crossword instructions
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES)

    def __str__(self):
        return self.question_text


class Crossword(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='crossword')
    grid = models.TextField()  # Can store the crossword grid as a serialized string (JSON format)
    across_clues = models.TextField()
    down_clues = models.TextField()
    
    def __str__(self):
        return f"Crossword for Question: {self.question.id}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text


class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    selected_choice = models.ForeignKey(Choice, blank=True, null=True, on_delete=models.CASCADE)
    crossword_solution = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user} - {self.question}'
