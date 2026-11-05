
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.generics import ListAPIView

from lessons.models import Lesson
from courses.models import Course
from enrollments.models import Enrollment
from .models import LessonProgress
from .serializers import LessonProgressSerializer



class MarkLessonCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        if request.user.role != "STUDENT":
            raise PermissionDenied("Only students can access this feature.")

        lesson = get_object_or_404(
            Lesson,
            id=lesson_id,
            is_published=True,
            course__is_published=True
        )

        enrollment = get_object_or_404(
            Enrollment,
            student=request.user,
            course=lesson.course,
            status="ACTIVE"
        )

        progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson,
            defaults={
                "course": lesson.course,
                "is_completed": True,
                "completed_at": timezone.now(),
            }
        )

        if not created and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()

        total_lessons = Lesson.objects.filter(
            course=lesson.course,
            is_published=True
        ).count()

        completed_lessons = LessonProgress.objects.filter(
            student=request.user,
            course=lesson.course,
            lesson__is_published=True,
            is_completed=True
        ).count()

        course_completed = (
            total_lessons > 0
            and completed_lessons >= total_lessons
        )

        if course_completed:
            enrollment.status = "COMPLETED"
            enrollment.save(update_fields=["status", "updated_at"])

        return Response({
            "message": "Lesson marked as completed.",
            "lesson": lesson.title,
            "is_completed": progress.is_completed,
            "completed_at": progress.completed_at,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "course_completed": course_completed,
        }, status=status.HTTP_200_OK)

class MyLearningProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "STUDENT":
            raise PermissionDenied("Only students can access this feature.")

        enrollments = Enrollment.objects.filter(
            student=request.user,
            status__in=["ACTIVE", "COMPLETED"]
        ).select_related("course")

        results = []

        for enrollment in enrollments:
            course = enrollment.course

            total_lessons = Lesson.objects.filter(
                course=course,
                is_published=True
            ).count()

            completed_lessons = LessonProgress.objects.filter(
                student=request.user,
                course=course,
                lesson__is_published=True,
                is_completed=True
            ).count()

            percentage = (
                round((completed_lessons / total_lessons) * 100, 2)
                if total_lessons > 0 else 0
            )

            results.append({
                "course_id": course.id,
                "course_title": course.title,
                "total_lessons": total_lessons,
                "completed_lessons": completed_lessons,
                "progress_percentage": percentage,
            })

        return Response(results)


class CourseProgressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        if request.user.role == "STUDENT":
            student = request.user

            enrolled = Enrollment.objects.filter(
                student=student,
                course=course,
                status__in=["ACTIVE", "COMPLETED"]
            ).exists()

            if not enrolled:
                raise PermissionDenied(
                    "You are not enrolled in this course."
                )

        elif request.user.role == "TRAINER":
            if course.trainer != request.user:
                raise PermissionDenied("You cannot view this course.")

            student_id = request.query_params.get("student")

            if not student_id:
                return Response(
                    {"error": "Please provide a student ID."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            student = get_object_or_404(
                Enrollment,
                student_id=student_id,
                course=course
            ).student

        elif request.user.role == "ADMIN":
            student_id = request.query_params.get("student")

            if not student_id:
                return Response(
                    {"error": "Please provide a student ID."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            enrollment = get_object_or_404(
                Enrollment,
                student_id=student_id,
                course=course
            )

            student = enrollment.student

        else:
            raise PermissionDenied("You do not have permission.")

        progress = LessonProgress.objects.filter(
            student=student,
            course=course
        ).select_related("lesson", "course", "student")

        serializer = LessonProgressSerializer(progress, many=True)

        return Response(serializer.data)


class TrainerCourseProgressView(ListAPIView):
    serializer_class = LessonProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return LessonProgress.objects.all().select_related(
                "student", "course", "lesson"
            )

        if user.role == "TRAINER":
            return LessonProgress.objects.filter(
                course__trainer=user
            ).select_related("student", "course", "lesson")

        raise PermissionDenied(
            "Only trainers and administrators can access reports."
        )
