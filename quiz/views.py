from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import Question, UserResponse, Choice
import json
from datetime import timedelta

QUESTION_DURATION = timedelta(minutes=10)

def quiz_home(request):
    return render(request, 'quiz/quiz_home.html')

def get_next_question(user):
    time_since_start = now()

    questions_passed = time_since_start // QUESTION_DURATION
    questions = Question.objects.all().order_by('id')

    answered_questions = UserResponse.objects.filter(user=user).values_list('question', flat=True)

    next_question = questions.exclude(id__in=answered_questions)[questions_passed:]

    return next_question.first()

@login_required
def start_quiz(request):
    next_question = get_next_question(request.user)

    if not next_question:
        return redirect('quiz_finished')

    return redirect('display_question', question_id=next_question.id)

@login_required
def display_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    time_since_start = now()
    questions_passed = time_since_start // QUESTION_DURATION

    question_position = list(Question.objects.all().order_by('id')).index(question)
    if question_position < questions_passed:
        return redirect('quiz_finished')

    if request.method == 'POST':
        if question.question_type == 'mcq':
            selected_choice = get_object_or_404(Choice, id=request.POST.get('choice'))
            UserResponse.objects.create(user=request.user, question=question, selected_choice=selected_choice)
        elif question.question_type == 'crossword':
            user_solution = request.POST.get('crossword_solution')
            UserResponse.objects.create(user=request.user, question=question, answer_text=user_solution)  # Use answer_text for crossword solutions
        else:
            UserResponse.objects.create(user=request.user, question=question, answer_text=request.POST.get('answer'))

        next_question = get_next_question(request.user)

        if next_question:
            return redirect('display_question', question_id=next_question.id)
        else:
            return redirect('quiz_finished')

    if question.question_type == 'crossword':
        # For crossword questions, assume the crossword clues and grid are managed here
        context = {
            'question': question,
            # Include crossword-specific context if needed
        }
        return render(request, 'quiz/crossword.html', context)

    context = {
        'question': question
    }
    return render(request, 'quiz/question.html', context)

@login_required
def quiz_finished(request):
    return render(request, 'quiz/finished.html')
