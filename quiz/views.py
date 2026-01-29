from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Question, Choice, UserResponse, Leaderboard, QuizSettings
from datetime import datetime, timedelta
import pytz

IST = pytz.timezone('Asia/Kolkata')
MAX_POINTS = 100  # Maximum points for each question


def get_quiz_settings():
    """Get quiz settings from database"""
    return QuizSettings.get_settings()


def get_question_duration(question, settings):
    """Get duration for a specific question based on its type and length"""
    if question.question_type == 'mcq' and len(question.question_text) > settings.long_text_threshold:
        return settings.long_text_duration
    elif question.question_type == 'text':
        return settings.short_text_duration
    return settings.default_duration


def get_question_schedule(settings):
    """
    Calculate the start time for each question.
    Returns a list of (question, start_time, duration) tuples.
    This ensures all users are synchronized to the same question.
    """
    questions = Question.objects.all().order_by('id')
    schedule = []
    current_time = settings.start_time
    
    for question in questions:
        duration = get_question_duration(question, settings)
        schedule.append({
            'question': question,
            'start_time': current_time,
            'end_time': current_time + timedelta(seconds=duration),
            'duration': duration
        })
        current_time += timedelta(seconds=duration)
    
    return schedule


def get_current_question(settings):
    """
    Get the question that should be displayed right now based on the schedule.
    All users will get the same question at the same time.
    """
    now = timezone.now()
    schedule = get_question_schedule(settings)
    
    for item in schedule:
        if item['start_time'] <= now < item['end_time']:
            time_remaining = int((item['end_time'] - now).total_seconds())
            return item['question'], time_remaining, item['duration']
    
    return None, 0, 0

def quiz_home(request):
    return render(request, 'quiz/quiz_home.html')


@login_required
def start_quiz(request):
    """Entry point for the quiz - redirects to current synchronized question"""
    settings = get_quiz_settings()
    current_time = timezone.now()
    
    # Check if quiz is active
    if not settings.is_active:
        return render(request, 'quiz/not_started.html', {
            'quiz': {'title': settings.quiz_title, 'message': 'Quiz is not active yet.'}
        })
    
    # Check if quiz hasn't started yet
    if current_time < settings.start_time:
        return render(request, 'quiz/not_started.html', {
            'quiz': {'title': settings.quiz_title, 'start_time': settings.start_time}
        })
    
    # Check if quiz has ended
    if current_time > settings.end_time:
        return redirect('quiz:quiz_finished')
    
    # Get the current synchronized question
    current_question, time_remaining, duration = get_current_question(settings)
    
    if not current_question:
        return redirect('quiz:quiz_finished')
    
    return redirect('quiz:display_question', question_id=current_question.id)


@login_required
def display_question(request, question_id):
    settings = get_quiz_settings()
    current_time = timezone.now()
    
    # Check if quiz is active and within time bounds
    if not settings.is_active or current_time < settings.start_time:
        return redirect('quiz:start_quiz')
    
    if current_time > settings.end_time:
        return redirect('quiz:quiz_finished')
    
    # Get the question that SHOULD be displayed right now (synchronized)
    current_question, time_remaining, duration = get_current_question(settings)
    
    if not current_question:
        return redirect('quiz:quiz_finished')
    
    # IMPORTANT: Enforce synchronization - redirect if user tries to access wrong question
    requested_question = get_object_or_404(Question, id=question_id)
    if requested_question.id != current_question.id:
        return redirect('quiz:display_question', question_id=current_question.id)
    
    question = current_question
    questions = list(Question.objects.all().order_by('id'))
    question_index = questions.index(question)
    next_question = questions[question_index + 1] if question_index + 1 < len(questions) else None
    
    # Handle answer submission
    if request.method == 'POST' and not UserResponse.objects.filter(user=request.user, question=question).exists():
        points = min(MAX_POINTS, max(0, int((time_remaining / duration) * MAX_POINTS)))
        
        if question.question_type == 'mcq':
            choice_id = request.POST.get('choice')
            if choice_id:
                selected_choice = get_object_or_404(Choice, id=choice_id)
                UserResponse.objects.create(user=request.user, question=question, selected_choice=selected_choice)
                if selected_choice.is_correct:
                    update_leaderboard_points(request.user, points)
        else:
            user_answer = request.POST.get('answer', '')
            UserResponse.objects.create(user=request.user, question=question, answer_text=user_answer)
            if user_answer and question.correct_answer:
                if user_answer.lower().strip() == question.correct_answer.lower().strip():
                    update_leaderboard_points(request.user, points)

        return HttpResponseRedirect(reverse('quiz:display_question', args=[question_id]))

    # Check if user already answered this question
    user_response = UserResponse.objects.filter(user=request.user, question=question).first()
    already_answered = user_response is not None

    leaderboard_entry = Leaderboard.objects.get_or_create(user=request.user, defaults={'points': 0})[0]
    leaderboard = Leaderboard.objects.all().order_by('-points')
    user_rank = list(leaderboard).index(leaderboard_entry) + 1

    context = {
        'question': question,
        'question_number': question_index + 1,
        'total_questions': len(questions),
        'time_remaining': time_remaining,
        'next_question': next_question,
        'correct_answer': question.correct_answer,
        'explanation': question.explanation,
        'rank': user_rank,
        'already_answered': already_answered,
    }
    return render(request, 'quiz/question.html', context)

@login_required
def leaderboard(request):
    leaderboard = Leaderboard.objects.all().order_by('-points')
    ranked_leaderboard = [{'user': entry.user, 'points': entry.points, 'rank': i + 1} for i, entry in enumerate(leaderboard)]
    user_rank = next((entry['rank'] for entry in ranked_leaderboard if entry['user'] == request.user), None)
    return render(request, 'quiz/leaderboard.html', {'leaderboard': leaderboard, 'user_rank': user_rank})

@login_required
def quiz_finished(request):
    leaderboard = Leaderboard.objects.all().order_by('-points')
    return render(request, 'quiz/finished.html', {'leaderboard': leaderboard})

def update_leaderboard_points(user, points):
    leaderboard_entry, _ = Leaderboard.objects.get_or_create(user=user, defaults={'points': 0})
    leaderboard_entry.points += points
    leaderboard_entry.save()