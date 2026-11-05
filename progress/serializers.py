from rest_framework import serializers
from .models import LessonProgress


class LessonProgressSerializer(serializers.ModelSerializer):

    lesson_title = serializers.CharField(
        source="lesson.title",
        read_only=True
    )

    course_title = serializers.CharField(
        source="course.title",
        read_only=True
    )

    class Meta:
        model = LessonProgress
        fields = [
            "id",
            "student",
            "course",
            "course_title",
            "lesson",
            "lesson_title",
            "is_completed",
            "completed_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "student",
            "course",
            "completed_at",
            "updated_at",
        ]