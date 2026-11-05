from rest_framework import serializers
from .models import Course, CourseCategory


class CourseCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseCategory
        fields = [
            "id",
            "name",
            "description",
            "created_at",
        ]


class CourseSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    trainer_name = serializers.CharField(
        source="trainer.username",
        read_only=True
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "category",
            "category_name",
            "trainer",
            "trainer_name",
            "title",
            "description",
            "thumbnail",
            "level",
            "duration_hours",
            "price",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
    "id",
    "trainer",
    "created_at",
    "updated_at",
]