
from rest_framework import serializers
from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(
        source="student.username",
        read_only=True
    )

    course_title = serializers.CharField(
        source="course.title",
        read_only=True
    )

    issued_by_name = serializers.CharField(
        source="issued_by.username",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Certificate
        fields = [
            "id",
            "student",
            "student_name",
            "course",
            "course_title",
            "certificate_number",
            "certificate_file",
            "issued_by",
            "issued_by_name",
            "issued_at",
        ]

        read_only_fields = [
            "id",
            "student",
            "certificate_number",
            "issued_by",
            "issued_at",
        ]
