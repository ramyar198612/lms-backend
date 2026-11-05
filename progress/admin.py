from django.contrib import admin
from .models import LessonProgress


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "student",
        "course",
        "lesson",
        "is_completed",
        "completed_at",
    )

    list_filter = ("is_completed", "course")

    search_fields = (
        "student__username",
        "course__title",
        "lesson__title",
    )