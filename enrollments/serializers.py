from rest_framework import serializers
from .models import Enrollment


class EnrollmentSerializer(serializers.ModelSerializer):

    course_title = serializers.CharField(
        source="course.title",
        read_only=True
    )

    student_name = serializers.CharField(
        source="student.username",
        read_only=True
    )

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "student_name",
            "course",
            "course_title",
            "status",
            "enrolled_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "student",
            "status",
            "enrolled_at",
            "updated_at",
        ]