from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from .models import Enrollment
from .serializers import EnrollmentSerializer
from courses.models import Course
from accounts.permissions import IsStudent


class CourseEnrollmentView(generics.CreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def perform_create(self, serializer):
        course_id = self.request.data.get("course")

        try:
            course = Course.objects.get(
                id=course_id,
                is_published=True
            )
        except (Course.DoesNotExist, ValueError, TypeError):
            raise ValidationError("Course is not available for enrollment.")

        if Enrollment.objects.filter(
            student=self.request.user,
            course=course
        ).exists():
            raise ValidationError("You are already enrolled in this course.")

        serializer.save(
            student=self.request.user,
            course=course
        )


class MyEnrollmentsView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related("student", "course")