from django.urls import path
from . import views

urlpatterns = [
    path('', views.quiz_home, name='quiz_home'),
    path('start/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('<int:quiz_id>/question/<int:question_id>/', views.display_question, name='display_question'),
    path('<int:quiz_id>/finished/', views.quiz_finished, name='quiz_finished'),
]
