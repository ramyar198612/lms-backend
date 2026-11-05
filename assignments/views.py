from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Assignment, AssignmentSubmission
from .serializers import (
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
    SubmissionReviewSerializer,
)
from courses.models import Course
from enrollments.models import Enrollment


class AssignmentListCreateView(generics.ListCreateAPIView):

    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get("course")

        queryset = Assignment.objects.select_related(
            "course", "course__trainer"
        )

        if not course_id:
            return queryset.none()

        if user.role == "ADMIN":
            return queryset.filter(course_id=course_id)

        if user.role == "TRAINER":
            return queryset.filter(
                course_id=course_id,
                course__trainer=user
            )

        if user.role == "STUDENT":
            enrolled = Enrollment.objects.filter(
                student=user,
                course_id=course_id,
                status__in=["ACTIVE", "COMPLETED"]
            ).exists()

            if enrolled:
                return queryset.filter(
                    course_id=course_id,
                    course__is_published=True,
                    is_published=True
                )

        return queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        course_id = self.request.data.get("course")

        try:
            course = Course.objects.get(id=course_id)
        except (Course.DoesNotExist, ValueError, TypeError):
            raise ValidationError("Course not found.")

        if user.role == "ADMIN":
            pass
        elif user.role == "TRAINER" and course.trainer_id == user.id:
            pass
        else:
            raise PermissionDenied(
                "Only the course trainer or administrator can create assignments."
            )

        lesson = serializer.validated_data.get("lesson")

        if lesson and lesson.course_id != course.id:
            raise ValidationError(
                "The selected lesson does not belong to this course."
            )

        serializer.save(course=course)


class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return Assignment.objects.all()

        if user.role == "TRAINER":
            return Assignment.objects.filter(course__trainer=user)

        if user.role == "STUDENT":
            return Assignment.objects.filter(
                course__is_published=True,
                is_published=True,
                course__enrollments__student=user,
                course__enrollments__status__in=["ACTIVE", "COMPLETED"]
            ).distinct()

        return Assignment.objects.none()

    def get_object(self):
        assignment = super().get_object()

        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return assignment

        user = self.request.user

        if user.role == "ADMIN":
            return assignment

        if user.role == "TRAINER" and assignment.course.trainer_id == user.id:
            return assignment

        raise PermissionDenied(
            "Only the course trainer or administrator can modify assignments."
        )


class AssignmentSubmissionCreateView(generics.CreateAPIView):

    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can submit assignments."
            )

        assignment_id = self.request.data.get("assignment")

        try:
            assignment = Assignment.objects.get(
                id=assignment_id,
                is_published=True,
                course__is_published=True
            )
        except (Assignment.DoesNotExist, ValueError, TypeError):
            raise ValidationError("Assignment is not available.")

        enrolled = Enrollment.objects.filter(
            student=user,
            course=assignment.course,
            status__in=["ACTIVE", "COMPLETED"]
        ).exists()

        if not enrolled:
            raise PermissionDenied(
                "You must be enrolled in this course."
            )

        if assignment.due_date and timezone.now() > assignment.due_date:
            raise ValidationError("Assignment submission deadline has passed.")

        if not self.request.data.get("answer_text") and not self.request.FILES.get("submission_file"):
            raise ValidationError(
                "Provide an answer or upload a submission file."
            )

        if AssignmentSubmission.objects.filter(
            assignment=assignment,
            student=user
        ).exists():
            raise ValidationError(
                "You have already submitted this assignment."
            )

        serializer.save(
            assignment=assignment,
            student=user
        )


class MySubmissionsView(generics.ListAPIView):

    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "STUDENT":
            return AssignmentSubmission.objects.filter(
                student=user
            ).select_related("assignment", "student")

        if user.role == "TRAINER":
            return AssignmentSubmission.objects.filter(
                assignment__course__trainer=user
            ).select_related("assignment", "student")

        if user.role == "ADMIN":
            return AssignmentSubmission.objects.all().select_related(
                "assignment", "student"
            )

        return AssignmentSubmission.objects.none()

class SubmissionReviewView(generics.UpdateAPIView):

    serializer_class = SubmissionReviewSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return AssignmentSubmission.objects.all()

        if user.role == "TRAINER":
            return AssignmentSubmission.objects.filter(
                assignment__course__trainer=user
            )

        return AssignmentSubmission.objects.none()

    def perform_update(self, serializer):
        user = self.request.user

        if user.role not in ["ADMIN", "TRAINER"]:
            raise PermissionDenied(
                "Only trainers and administrators can review submissions."
            )

        submission = self.get_object()

        if user.role == "TRAINER" and submission.assignment.course.trainer_id != user.id:
            raise PermissionDenied(
                "You cannot review submissions for another trainer's course."
            )

        marks = serializer.validated_data.get(
            "marks_obtained",
            submission.marks_obtained
        )

        feedback = serializer.validated_data.get(
            "feedback",
            submission.feedback
        )

        if marks is None:
            raise ValidationError("Marks are required for review.")

        if marks > submission.assignment.total_marks:
            raise ValidationError(
                "Marks cannot exceed the assignment total marks."
            )

        serializer.save(
            status=AssignmentSubmission.Status.REVIEWED,
            marks_obtained=marks,
            feedback=feedback
        )
