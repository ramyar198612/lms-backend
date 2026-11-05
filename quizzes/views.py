from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import (
    Quiz,
    Question,
    Choice,
    QuizAttempt,
    QuizAnswer,
)
from .serializers import (
    QuizSerializer,
    QuestionCreateSerializer,
    QuizAnswerSubmitSerializer,
    QuizAttemptResultSerializer,
    QuizAnswerResultSerializer,
)

from courses.models import Course
from enrollments.models import Enrollment


class QuizListCreateView(generics.ListCreateAPIView):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get("course")

        if not course_id:
            return Quiz.objects.none()

        queryset = Quiz.objects.filter(
            course_id=course_id
        ).prefetch_related("questions__choices")

        if user.role == "ADMIN":
            return queryset

        if user.role == "TRAINER":
            return queryset.filter(course__trainer=user)

        if user.role == "STUDENT":
            enrolled = Enrollment.objects.filter(
                student=user,
                course_id=course_id,
                status__in=["ACTIVE", "COMPLETED"]
            ).exists()

            if enrolled:
                return queryset.filter(
                    course__is_published=True,
                    is_published=True
                )

        return Quiz.objects.none()

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
                "Only the course trainer or administrator can create quizzes."
            )

        lesson = serializer.validated_data.get("lesson")

        if lesson and lesson.course_id != course.id:
            raise ValidationError(
                "The selected lesson does not belong to this course."
            )

        serializer.save(course=course)


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return Quiz.objects.all()

        if user.role == "TRAINER":
            return Quiz.objects.filter(course__trainer=user)

        if user.role == "STUDENT":
            return Quiz.objects.filter(
                is_published=True,
                course__is_published=True,
                course__enrollments__student=user,
                course__enrollments__status__in=["ACTIVE", "COMPLETED"]
            ).distinct()

        return Quiz.objects.none()

    def get_object(self):
        quiz = super().get_object()

        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return quiz

        user = self.request.user

        if user.role == "ADMIN":
            return quiz

        if user.role == "TRAINER" and quiz.course.trainer_id == user.id:
            return quiz

        raise PermissionDenied("You cannot modify this quiz.")


class QuestionCreateView(generics.CreateAPIView):
    serializer_class = QuestionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        quiz_id = self.request.data.get("quiz")

        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except (Quiz.DoesNotExist, ValueError, TypeError):
            raise ValidationError("Quiz not found.")

        if user.role == "ADMIN":
            pass
        elif user.role == "TRAINER" and quiz.course.trainer_id == user.id:
            pass
        else:
            raise PermissionDenied(
                "Only the quiz trainer or administrator can add questions."
            )

        question = serializer.save(quiz=quiz)

        quiz.total_marks = quiz.questions.aggregate(
            total=Sum("marks")
        )["total"] or 0

        quiz.save(update_fields=["total_marks"])


class QuizStartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user = request.user

        if user.role != "STUDENT":
            raise PermissionDenied("Only students can attempt quizzes.")

        try:
            quiz = Quiz.objects.get(
                id=pk,
                is_published=True,
                course__is_published=True
            )
        except Quiz.DoesNotExist:
            raise ValidationError("Quiz is not available.")

        enrolled = Enrollment.objects.filter(
            student=user,
            course=quiz.course,
            status__in=["ACTIVE", "COMPLETED"]
        ).exists()

        if not enrolled:
            raise PermissionDenied(
                "You must be enrolled in this course."
            )

        if not quiz.questions.exists():
            raise ValidationError("This quiz has no questions.")

        previous_attempts = QuizAttempt.objects.filter(
            quiz=quiz,
            student=user
        )

        attempt_number = previous_attempts.count() + 1

        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=user,
            attempt_number=attempt_number,
            total_marks=quiz.total_marks
        )

        return Response({
            "message": "Quiz started successfully.",
            "attempt_id": attempt.id,
            "quiz": quiz.title,
            "duration_minutes": quiz.duration_minutes,
            "questions": [
                {
                    "id": question.id,
                    "question_text": question.question_text,
                    "marks": question.marks,
                    "choices": [
                        {
                            "id": choice.id,
                            "choice_text": choice.choice_text
                        }
                        for choice in question.choices.all()
                    ]
                }
                for question in quiz.questions.prefetch_related("choices").all()
            ]
        })


class QuizSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        user = request.user

        if user.role != "STUDENT":
            raise PermissionDenied("Only students can submit quizzes.")

        try:
            attempt = QuizAttempt.objects.select_for_update().get(
                id=pk,
                student=user,
                status=QuizAttempt.Status.IN_PROGRESS
            )
        except QuizAttempt.DoesNotExist:
            raise ValidationError("Active quiz attempt not found.")

        elapsed = (timezone.now() - attempt.started_at).total_seconds()

        if elapsed > attempt.quiz.duration_minutes * 60:
            raise ValidationError("Quiz time has expired.")

        answers = request.data.get("answers")

        if not isinstance(answers, list) or not answers:
            raise ValidationError("Please submit your quiz answers.")

        if QuizAnswer.objects.filter(attempt=attempt).exists():
            raise ValidationError("This quiz has already been submitted.")

        score = 0
        answered_questions = set()

        for answer_data in answers:
            serializer = QuizAnswerSubmitSerializer(data=answer_data)
            serializer.is_valid(raise_exception=True)

            question_id = serializer.validated_data["question"]
            choice_id = serializer.validated_data["selected_choice"]

            if question_id in answered_questions:
                raise ValidationError("Duplicate question answer.")

            answered_questions.add(question_id)

            try:
                question = attempt.quiz.questions.get(id=question_id)
            except Question.DoesNotExist:
                raise ValidationError("Invalid question for this quiz.")

            try:
                choice = question.choices.get(id=choice_id)
            except Choice.DoesNotExist:
                raise ValidationError("Invalid answer choice for this question.")

            correct = choice.is_correct
            marks = question.marks if correct else 0

            score += marks

            QuizAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=choice,
                is_correct=correct,
                marks_obtained=marks
            )

        attempt.score = score
        attempt.passed = score >= attempt.quiz.passing_marks
        attempt.status = QuizAttempt.Status.COMPLETED
        attempt.completed_at = timezone.now()
        attempt.save()

        return Response({
            "message": "Quiz submitted successfully.",
            "score": score,
            "total_marks": attempt.total_marks,
            "passed": attempt.passed
        })



class MyQuizResultsView(generics.ListAPIView):
    serializer_class = QuizAttemptResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "STUDENT":
            return QuizAttempt.objects.filter(
                student=user,
                status=QuizAttempt.Status.COMPLETED
            ).select_related("quiz")

        if user.role == "TRAINER":
            return QuizAttempt.objects.filter(
                quiz__course__trainer=user,
                status=QuizAttempt.Status.COMPLETED
            ).select_related("quiz", "student")

        if user.role == "ADMIN":
            return QuizAttempt.objects.filter(
                status=QuizAttempt.Status.COMPLETED
            ).select_related("quiz", "student")

        return QuizAttempt.objects.none()


class QuizResultDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = request.user

        try:
            attempt = QuizAttempt.objects.select_related(
                "quiz", "quiz__course"
            ).get(
                id=pk,
                status=QuizAttempt.Status.COMPLETED
            )
        except QuizAttempt.DoesNotExist:
            raise ValidationError("Quiz result not found.")

        if user.role == "STUDENT" and attempt.student_id != user.id:
            raise PermissionDenied("You cannot view another student's result.")

        if (
            user.role == "TRAINER"
            and attempt.quiz.course.trainer_id != user.id
        ):
            raise PermissionDenied("You cannot view this quiz result.")

        if user.role not in ["STUDENT", "TRAINER", "ADMIN"]:
            raise PermissionDenied("You do not have permission.")

        return Response({
            "result": QuizAttemptResultSerializer(attempt).data,
            "answers": QuizAnswerResultSerializer(
                attempt.answers.select_related(
                    "question", "selected_choice"
                ),
                many=True
            ).data
        })