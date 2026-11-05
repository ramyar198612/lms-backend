from rest_framework import serializers
from .models import Assignment, AssignmentSubmission


class AssignmentSerializer(serializers.ModelSerializer):

    course_title = serializers.CharField(
        source="course.title",
        read_only=True
    )

    class Meta:
        model = Assignment
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class AssignmentSubmissionSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(
        source="student.username",
        read_only=True
    )

    assignment_title = serializers.CharField(
        source="assignment.title",
        read_only=True
    )

    class Meta:
        model = AssignmentSubmission
        fields = "__all__"
        read_only_fields = [
            "id",
            "student",
            "marks_obtained",
            "feedback",
            "status",
            "submitted_at",
            "updated_at",
        ]
class SubmissionReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignmentSubmission
        fields = ["marks_obtained", "feedback"]

    def validate_marks_obtained(self, value):
        assignment = self.instance.assignment

        if value > assignment.total_marks:
            raise serializers.ValidationError(
                f"Marks cannot exceed {assignment.total_marks}."
            )

        return value

    def update(self, instance, validated_data):
        instance.marks_obtained = validated_data["marks_obtained"]
        instance.feedback = validated_data.get(
            "feedback", instance.feedback
        )
        instance.status = AssignmentSubmission.Status.REVIEWED
        instance.save()

        return instance