from django.urls import path
from . import views

urlpatterns = [
    path('', views.quiz_home, name='quiz_home'),  # Homepage for the quiz (optional)
    path('start/<int:quiz_id>/', views.start_quiz, name='start_quiz'),  # Start the quiz
    path('<int:quiz_id>/question/<int:question_id>/', views.display_question, name='display_question'),  # Display a quiz question
    path('<int:quiz_id>/finished/', views.quiz_finished, name='quiz_finished'),  # Show the quiz finished page
]
