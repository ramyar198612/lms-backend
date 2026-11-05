from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Lesson
from .serializers import LessonSerializer
from courses.models import Course
from enrollments.models import Enrollment


class LessonListCreateView(generics.ListCreateAPIView):

    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        course_id = self.request.query_params.get("course")

        queryset = Lesson.objects.select_related(
            "course",
            "course__trainer"
        )

        if not course_id:
            return queryset.none()

        user = self.request.user

        if not user.is_authenticated:
            return queryset.filter(
                course_id=course_id,
                course__is_published=True,
                is_published=True
            )

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
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Course not found.")

        if user.role == "ADMIN":
            pass

        elif user.role == "TRAINER" and course.trainer_id == user.id:
            pass

        else:
            raise PermissionDenied(
                "Only the course trainer or administrator can create lessons."
            )

        serializer.save(course=course)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Lesson.objects.filter(
                is_published=True,
                course__is_published=True
            )

        if user.role == "ADMIN":
            return Lesson.objects.all()

        if user.role == "TRAINER":
            return Lesson.objects.filter(
                course__trainer=user
            )

        if user.role == "STUDENT":
            return Lesson.objects.filter(
                course__is_published=True,
                is_published=True,
                course__enrollments__student=user,
                course__enrollments__status__in=["ACTIVE", "COMPLETED"]
            ).distinct()

        return Lesson.objects.none()

    def get_object(self):
        lesson = super().get_object()

        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return lesson

        user = self.request.user

        if user.role == "ADMIN":
            return lesson

        if (
            user.role == "TRAINER"
            and lesson.course.trainer_id == user.id
        ):
            return lesson

        raise PermissionDenied(
            "You cannot modify this lesson."
        )