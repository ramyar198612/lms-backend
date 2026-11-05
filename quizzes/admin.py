from django.contrib import admin
from .models import (
    Quiz,
    Question,
    Choice,
    QuizAttempt,
    QuizAnswer,
)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "course",
        "total_marks",
        "passing_marks",
        "is_published",
    )

    list_filter = ("is_published", "course")
    search_fields = ("title", "course__title")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "question_text", "quiz", "marks", "order")
    list_filter = ("quiz",)
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "choice_text", "is_correct")
    list_filter = ("is_correct",)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "quiz",
        "student",
        "attempt_number",
        "score",
        "passed",
        "status",
    )

    list_filter = ("status", "passed")


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "attempt",
        "question",
        "selected_choice",
        "is_correct",
        "marks_obtained",
    )