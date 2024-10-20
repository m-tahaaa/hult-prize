from django.urls import path
from . import views

urlpatterns = [
    path('quiz/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/question/<int:question_id>/', views.display_question, name='display_question'),
    path('quiz/<int:quiz_id>/finished/', views.quiz_finished, name='quiz_finished'),
]