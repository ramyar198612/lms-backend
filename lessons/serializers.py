from rest_framework import serializers
from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):

    course_title = serializers.CharField(
        source="course.title",
        read_only=True
    )

    trainer_name = serializers.CharField(
        source="course.trainer.username",
        read_only=True
    )

    class Meta:
        model = Lesson

        fields = [
            "id",
            "course",
            "course_title",
            "trainer_name",
            "title",
            "description",
            "lesson_type",
            "content",
            "video_file",
            "pdf_file",
            "duration_minutes",
            "order",
            "is_published",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "course_title",
            "trainer_name",
        ]