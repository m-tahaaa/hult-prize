from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Choice)
admin.site.register(UserResponse)
admin.site.register(Leaderboard)

class Answeradmin(admin.StackedInline):
    model=Choice

class QuestionAdmin(admin.ModelAdmin):
    inlines=[Answeradmin]

admin.site.register(Question,QuestionAdmin)


@admin.register(QuizSettings)
class QuizSettingsAdmin(admin.ModelAdmin):
    list_display = ('quiz_title', 'start_time', 'end_time', 'is_active')
    fieldsets = (
        ('Quiz Info', {
            'fields': ('quiz_title', 'is_active')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Question Durations (seconds)', {
            'fields': ('default_duration', 'short_text_duration', 'long_text_duration', 'long_text_threshold'),
            'description': 'Configure how long each question type is displayed'
        }),
    )

