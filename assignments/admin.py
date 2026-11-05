from django.contrib import admin
from .models import Assignment, AssignmentSubmission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "course",
        "total_marks",
        "due_date",
        "is_published",
    )
    list_filter = ("is_published", "course")
    search_fields = ("title", "course__title")


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "student",
        "marks_obtained",
        "status",
        "submitted_at",
    )
    list_filter = ("status", "submitted_at")
    search_fields = (
        "student__username",
        "assignment__title",
    )