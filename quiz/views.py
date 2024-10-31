from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import *
from datetime import datetime, timedelta
from django.utils import timezone

QUIZ_START_TIME = timezone.make_aware(datetime.now().replace(hour=15, minute=0, second=0, microsecond=0))
MAX_POINTS = 10
QUESTION_DURATION = timedelta(minutes=1)

# Home page for the quiz
def quiz_home(request):
    return render(request, 'quiz/quiz_home.html')

# Calculate the current question based on elapsed time
def calculate_current_question():
    time_elapsed = now() - QUIZ_START_TIME
    questions_passed = time_elapsed // QUESTION_DURATION
    return max(0, int(questions_passed))

# Function to get the next unanswered question for the user
def get_next_question(user):
    current_question_number = calculate_current_question()
    answered_questions = UserResponse.objects.filter(user=user).values_list('question', flat=True)
    questions = Question.objects.all().order_by('id').exclude(id__in=answered_questions)

    if current_question_number >= len(questions):
        return None
    
    return questions[current_question_number]

# Start the quiz
@login_required
def start_quiz(request):
    first_question = get_next_question(request.user)
    if first_question:
        return redirect('display_question', question_id=first_question.id)
    else:
        return redirect('quiz_finished')

# Display a question and handle responses
@login_required
def display_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    current_question_number = calculate_current_question()
    question_position = list(Question.objects.all().order_by('id')).index(question)
    
    if question_position < current_question_number:
        return redirect('quiz_finished')
    
    question_start_time = QUIZ_START_TIME + timedelta(seconds=question_position * QUESTION_DURATION.total_seconds())

    if request.method == 'POST':
        time_answered = now()
        elapsed_time_s = (time_answered - question_start_time).total_seconds()

        # Calculate points based on response time
        if elapsed_time_s <= QUESTION_DURATION.total_seconds():
            points = int((1 - (elapsed_time_s / QUESTION_DURATION.total_seconds())) * MAX_POINTS)
        else:
            points = 0  # No points if answered after the question duration

        # Process response based on question type
        if question.question_type == 'mcq':
            selected_choice = get_object_or_404(Choice, id=request.POST.get('choice'))
            UserResponse.objects.create(user=request.user, question=question, selected_choice=selected_choice, submission_time=time_answered)
            if selected_choice.is_correct:
                update_leaderboard_points(request.user, points)
        else:
            user_answer = request.POST.get('answer')
            UserResponse.objects.create(user=request.user, question=question, answer_text=user_answer, submission_time=time_answered)
            if user_answer == question.correct_answer:
                update_leaderboard_points(request.user, points)

        next_question = get_next_question(request.user)
        if next_question:
            return redirect('display_question', question_id=next_question.id)
        else:
            return redirect('quiz_finished')

    context = {
        'question': question,
        'leaderboard': Leaderboard.objects.all().order_by('-points'),
        'time_remaining': QUESTION_DURATION.total_seconds() - (now() - question_start_time).total_seconds()
    }
    return render(request, 'quiz/question.html', context)

# Display the leaderboard after quiz completion
@login_required
def quiz_finished(request):
    leaderboard = Leaderboard.objects.all().order_by('-points')
    return render(request, 'quiz/finished.html', {'leaderboard': leaderboard})

# Update leaderboard points based on response time
def update_leaderboard_points(user, points):
    leaderboard_entry, created = Leaderboard.objects.get_or_create(user=user, defaults={'points': 0})
    leaderboard_entry.points += points
    leaderboard_entry.save()
