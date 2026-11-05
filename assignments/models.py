from django.db import models
from django.conf import settings
from courses.models import Course
from lessons.models import Lesson


class Assignment(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments"
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    attachment = models.FileField(
        upload_to="assignments/files/",
        null=True,
        blank=True
    )

    total_marks = models.PositiveIntegerField(default=100)
    due_date = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):

    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        REVIEWED = "REVIEWED", "Reviewed"

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_submissions"
    )

    answer_text = models.TextField(blank=True)

    submission_file = models.FileField(
        upload_to="assignments/submissions/",
        null=True,
        blank=True
    )

    marks_obtained = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    feedback = models.TextField(blank=True)

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.SUBMITTED
    )

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("assignment", "student")
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"