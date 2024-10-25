# hult-prize/quiz/urls.py
from django.urls import path
from .views import quiz_home, start_quiz, display_question, quiz_finished

urlpatterns = [
    path('', quiz_home, name='quiz_home'),
    path('start/', start_quiz, name='start_quiz'),
    path('question/<int:question_id>/', display_question, name='display_question'),
    path('finished/', quiz_finished, name='quiz_finished'),
]
