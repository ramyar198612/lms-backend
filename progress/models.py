from django.db import models
from django.conf import settings
from courses.models import Course
from lessons.models import Lesson


class LessonProgress(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="student_progress"
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="student_progress"
    )

    is_completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "lesson")
        ordering = ["lesson__order"]

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"