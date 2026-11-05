from django.db import models
from courses.models import Course


class Lesson(models.Model):

    class LessonType(models.TextChoices):
        TEXT = "TEXT", "Text"
        VIDEO = "VIDEO", "Video"
        PDF = "PDF", "PDF"

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    lesson_type = models.CharField(
        max_length=10,
        choices=LessonType.choices,
        default=LessonType.TEXT
    )

    content = models.TextField(blank=True)

    video_file = models.FileField(
        upload_to="lessons/videos/",
        null=True,
        blank=True
    )

    pdf_file = models.FileField(
        upload_to="lessons/pdfs/",
        null=True,
        blank=True
    )

    duration_minutes = models.PositiveIntegerField(default=0)

    order = models.PositiveIntegerField(default=1)

    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        unique_together = ("course", "order")

    def __str__(self):
        return f"{self.course.title} - {self.title}"