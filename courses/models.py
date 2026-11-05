from django.db import models


class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
from accounts.models import CustomUser


class Course(models.Model):

    class Level(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"

    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.PROTECT,
        related_name="courses"
    )

    trainer = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="created_courses",
        limit_choices_to={"role": "TRAINER"}
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(
        upload_to="courses/thumbnails/",
        null=True,
        blank=True
    )
    level = models.CharField(
        max_length=15,
        choices=Level.choices,
        default=Level.BEGINNER
    )
    duration_hours = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title