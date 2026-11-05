from django.db import models
from django.conf import settings
from courses.models import Course
from lessons.models import Lesson


class Quiz(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="quizzes"
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quizzes"
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    duration_minutes = models.PositiveIntegerField(default=30)

    total_marks = models.PositiveIntegerField(default=0)
    passing_marks = models.PositiveIntegerField(default=0)

    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):

    class QuestionType(models.TextChoices):
        MCQ = "MCQ", "Multiple Choice"

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question_text = models.TextField()

    question_type = models.CharField(
        max_length=10,
        choices=QuestionType.choices,
        default=QuestionType.MCQ
    )

    marks = models.PositiveIntegerField(default=1)

    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]
        unique_together = ("quiz", "order")

    def __str__(self):
        return self.question_text[:80]


class Choice(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices"
    )

    choice_text = models.CharField(max_length=500)

    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class QuizAttempt(models.Model):

    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts"
    )

    attempt_number = models.PositiveIntegerField(default=1)

    score = models.PositiveIntegerField(default=0)

    total_marks = models.PositiveIntegerField(default=0)

    passed = models.BooleanField(default=False)

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.IN_PROGRESS
    )

    started_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-started_at"]
        unique_together = ("quiz", "student", "attempt_number")

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"


class QuizAnswer(models.Model):

    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="student_answers"
    )

    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="selected_answers"
    )

    is_correct = models.BooleanField(default=False)

    marks_obtained = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("attempt", "question")

    def __str__(self):
        return f"Answer - {self.question}"