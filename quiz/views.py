from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import Question, UserResponse, Choice, Leaderboard
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
            if selected_choice.is_correct:
                update_leaderboard_points(request.user, 10)
        elif question.question_type == 'crossword':
            user_solution = request.POST.get('crossword_solution')
            UserResponse.objects.create(user=request.user, question=question, crossword_solution=user_solution)
            # Compare solution with correct answer
            if user_solution == question.correct_answer:
                update_leaderboard_points(request.user, 10)
        else:
            user_answer = request.POST.get('answer')
            UserResponse.objects.create(user=request.user, question=question, answer_text=user_answer)
            if user_answer == question.correct_answer:
                update_leaderboard_points(request.user, 10)

        next_question = get_next_question(request.user)

        if next_question:
            return redirect('display_question', question_id=next_question.id)
        else:
            return redirect('quiz_finished')

    if question.question_type == 'crossword':
        crossword = question.crossword
        grid = json.loads(crossword.grid)  # Serialized crossword grid
        across_clues = json.loads(crossword.across_clues)
        down_clues = json.loads(crossword.down_clues)
        context = {
            'question': question,
            'grid': grid,
            'across_clues': across_clues,
            'down_clues': down_clues,
            'leaderboard': Leaderboard.objects.all().order_by('-points'),  # Add leaderboard context
        }
        return render(request, 'quiz/crossword.html', context)

    context = {
        'question': question,
        'leaderboard': Leaderboard.objects.all().order_by('-points')  # Add leaderboard context
    }
    return render(request, 'quiz/question.html', context)

@login_required
def quiz_finished(request):
    leaderboard = Leaderboard.objects.all().order_by('-points')
    return render(request, 'quiz/finished.html', {'leaderboard': leaderboard})

def update_leaderboard_points(user, points):
    leaderboard_entry, created = Leaderboard.objects.get_or_create(user=user)
    leaderboard_entry.points += points
    leaderboard_entry.save()
