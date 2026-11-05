from django.contrib import admin
from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "course",
        "lesson_type",
        "order",
        "is_published",
        "created_at",
    )

    list_filter = ("lesson_type", "is_published", "course")

    search_fields = ("title", "course__title")

    ordering = ("course", "order")