
import uuid

from django.db import models
from django.conf import settings
from courses.models import Course


class Certificate(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="certificates"
    )

    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="issued_certificates"
    )

    certificate_number = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    certificate_file = models.FileField(
        upload_to="certificates/",
        null=True,
        blank=True
    )

    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course_certificate"
            )
        ]

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
