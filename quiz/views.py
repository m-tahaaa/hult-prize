from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, UserResponse, Choice
import datetime

def get_next_question(quiz, user):
    answered_questions = UserResponse.objects.filter(user=user, question__quiz=quiz).values_list('question', flat=True)
    return Question.objects.filter(quiz=quiz).exclude(id__in=answered_questions).first()

@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if now() < quiz.start_time:
        return render(request, 'quiz/not_started.html', {'quiz': quiz})

    next_question = get_next_question(quiz, request.user)
    
    if not next_question:
        return redirect('quiz_finished', quiz_id=quiz.id)
    
    return redirect('display_question', quiz_id=quiz.id, question_id=next_question.id)

@login_required
def display_question(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        if question.question_type == 'mcq':
            selected_choice = get_object_or_404(Choice, id=request.POST.get('choice'))
            UserResponse.objects.create(user=request.user, question=question, selected_choice=selected_choice)
        else:
            UserResponse.objects.create(user=request.user, question=question, answer_text=request.POST.get('answer'))
            
        next_question = get_next_question(quiz, request.user)
        
        if next_question:
            return redirect('display_question', quiz_id=quiz.id, question_id=next_question.id)
        else:
            return redirect('quiz_finished', quiz_id=quiz.id)

    context = {
        'quiz': quiz,
        'question': question
    }
    return render(request, 'quiz/question.html', context)

@login_required
def quiz_finished(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'quiz/finished.html', {'quiz': quiz})
