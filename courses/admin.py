from django.contrib import admin
from .models import CourseCategory, Course


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "trainer",
        "level",
        "price",
        "is_published",
    )

    list_filter = ("category", "level", "is_published")
    search_fields = ("title", "description")
    ordering = ("-created_at",)