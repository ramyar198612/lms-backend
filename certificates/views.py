
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied

from courses.models import Course
from enrollments.models import Enrollment
from accounts.models import CustomUser

from .models import Certificate
from .serializers import CertificateSerializer
from quizzes.models import QuizAttempt
from assignments.models import AssignmentSubmission


class MyCertificatesView(generics.ListAPIView):

    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can view their certificates."
            )

        return Certificate.objects.filter(
            student=self.request.user
        ).select_related("student", "course", "issued_by")


class IssueCertificateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user

        if user.role not in ["ADMIN", "TRAINER"]:
            raise PermissionDenied(
                "Only trainers and administrators can issue certificates."
            )

        student_id = request.data.get("student")
        course_id = request.data.get("course")

        if not student_id or not course_id:
            return Response(
                {"error": "Student ID and course ID are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        student = get_object_or_404(
            CustomUser,
            id=student_id,
            role="STUDENT"
        )

        course = get_object_or_404(Course, id=course_id)

        if user.role == "TRAINER" and course.trainer_id != user.id:
            raise PermissionDenied(
                "You can issue certificates only for your own courses."
            )

        enrollment = get_object_or_404(
            Enrollment,
            student=student,
            course=course
        )

        if enrollment.status != "COMPLETED":
            return Response(
                {
                    "error": "Certificate can only be issued after course completion."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        certificate, created = Certificate.objects.get_or_create(
            student=student,
            course=course,
            defaults={"issued_by": user}
        )

        if not created:
            return Response(
                {
                    "message": "Certificate has already been issued.",
                    "certificate": CertificateSerializer(certificate).data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "message": "Certificate issued successfully.",
                "certificate": CertificateSerializer(certificate).data
            },
            status=status.HTTP_201_CREATED
        )


class CertificateVerificationView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, certificate_number):

        certificate = get_object_or_404(
            Certificate.objects.select_related(
                "student", "course"
            ),
            certificate_number=certificate_number
        )

        return Response({
            "valid": True,
            "certificate_number": str(
                certificate.certificate_number
            ),
            "student_name": certificate.student.get_full_name()
            or certificate.student.username,
            "course_title": certificate.course.title,
            "issued_at": certificate.issued_at,
        })


class AllCertificatesView(generics.ListAPIView):

    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return Certificate.objects.all().select_related(
                "student", "course", "issued_by"
            )

        if user.role == "TRAINER":
            return Certificate.objects.filter(
                course__trainer=user
            ).select_related("student", "course", "issued_by")

        raise PermissionDenied(
            "Only trainers and administrators can view all certificates."
        )

class CoursePerformanceReportView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        if user.role == "ADMIN":
            courses = Course.objects.all()

        elif user.role == "TRAINER":
            courses = Course.objects.filter(trainer=user)

        else:
            raise PermissionDenied(
                "Only trainers and administrators can view course reports."
            )

        reports = []

        for course in courses:

            enrollments = Enrollment.objects.filter(course=course)

            total_students = enrollments.count()

            completed_students = enrollments.filter(
                status="COMPLETED"
            ).count()

            active_students = enrollments.filter(
                status="ACTIVE"
            ).count()

            reports.append({
                "course_id": course.id,
                "course_title": course.title,
                "total_students": total_students,
                "active_students": active_students,
                "completed_students": completed_students,
            })

        return Response(reports)



class StudentPerformanceReportView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        if user.role not in ["ADMIN", "TRAINER"]:
            raise PermissionDenied(
                "Only trainers and administrators can view student reports."
            )

        enrollments = Enrollment.objects.select_related(
            "student", "course"
        )

        if user.role == "TRAINER":
            enrollments = enrollments.filter(
                course__trainer=user
            )

        reports = []

        for enrollment in enrollments:

            quiz_attempts = QuizAttempt.objects.filter(
                student=enrollment.student,
                quiz__course=enrollment.course,
                status="COMPLETED"
            ).select_related("quiz")

            assignment_submissions = AssignmentSubmission.objects.filter(
                student=enrollment.student,
                assignment__course=enrollment.course
            ).select_related("assignment")

            reports.append({
                "student_id": enrollment.student_id,
                "student_name": enrollment.student.username,
                "course_id": enrollment.course_id,
                "course_title": enrollment.course.title,
                "enrollment_status": enrollment.status,
                "enrolled_at": enrollment.enrolled_at,

                "quiz_results": [
                    {
                        "quiz_title": attempt.quiz.title,
                        "score": attempt.score,
                        "total_marks": attempt.total_marks,
                        "passed": attempt.passed,
                    }
                    for attempt in quiz_attempts
                ],

                "assignment_results": [
                    {
                        "assignment_title": submission.assignment.title,
                        "marks_obtained": submission.marks_obtained,
                        "total_marks": submission.assignment.total_marks,
                        "status": submission.status,
                        "feedback": submission.feedback,
                    }
                    for submission in assignment_submissions
                ],
            })

        return Response(reports)
