
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied,ValidationError

from courses.models import Course
from enrollments.models import Enrollment
from .models import ForumTopic, ForumReply, LiveClass
from .serializers import (
    ForumTopicSerializer,
    ForumReplySerializer,
    LiveClassSerializer,
)


def can_access_course(user, course):
    if user.role == "ADMIN":
        return True

    if user.role == "TRAINER":
        return course.trainer_id == user.id

    if user.role == "STUDENT":
        return Enrollment.objects.filter(
            student=user,
            course=course,
            status__in=["ACTIVE", "COMPLETED"]
        ).exists()

    return False


class ForumTopicListCreateView(generics.ListCreateAPIView):
    serializer_class = ForumTopicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = ForumTopic.objects.select_related(
            "course", "created_by"
        ).prefetch_related("replies", "replies__created_by")

        if user.role == "ADMIN":
            return queryset

        if user.role == "TRAINER":
            return queryset.filter(course__trainer=user)

        if user.role == "STUDENT":
            enrolled_courses = Enrollment.objects.filter(
                student=user,
                status__in=["ACTIVE", "COMPLETED"]
            ).values_list("course_id", flat=True)

            return queryset.filter(course_id__in=enrolled_courses)

        return ForumTopic.objects.none()

    def perform_create(self, serializer):
        course = get_object_or_404(
            Course,
            id=self.request.data.get("course")
        )

        if not can_access_course(self.request.user, course):
            raise PermissionDenied(
                "You cannot access this course forum."
            )

        serializer.save(created_by=self.request.user)



class ForumTopicDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ForumTopicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return ForumTopic.objects.all()

        if user.role == "TRAINER":
            return ForumTopic.objects.filter(course__trainer=user)

        if user.role == "STUDENT":
            enrolled_courses = Enrollment.objects.filter(
                student=user,
                status__in=["ACTIVE", "COMPLETED"]
            ).values_list("course_id", flat=True)

            return ForumTopic.objects.filter(
                course_id__in=enrolled_courses
            )

        return ForumTopic.objects.none()

    def update(self, request, *args, **kwargs):
        topic = self.get_object()
        user = request.user

        if topic.created_by_id != user.id and user.role not in [
            "ADMIN", "TRAINER"
        ]:
            raise PermissionDenied("You cannot edit this topic.")

        if "course" in request.data:
            raise ValidationError(
                "A forum topic cannot be moved to another course."
            )

        if "is_closed" in request.data and user.role not in [
            "ADMIN", "TRAINER"
        ]:
            raise PermissionDenied(
                "Only trainers and administrators can close a topic."
            )

        if user.role == "TRAINER" and topic.course.trainer_id != user.id:
            raise PermissionDenied(
                "You cannot modify topics in another trainer's course."
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        topic = self.get_object()
        user = request.user

        if topic.created_by_id != user.id and user.role not in [
            "ADMIN", "TRAINER"
        ]:
            raise PermissionDenied("You cannot delete this topic.")

        if user.role == "TRAINER" and topic.course.trainer_id != user.id:
            raise PermissionDenied(
                "You cannot delete topics in another trainer's course."
            )

        return super().destroy(request, *args, **kwargs)

class ForumReplyListCreateView(generics.ListCreateAPIView):
    serializer_class = ForumReplySerializer
    permission_classes = [IsAuthenticated]

    def get_topic(self):
        topic = get_object_or_404(
            ForumTopic,
            id=self.kwargs["topic_id"]
        )

        if not can_access_course(self.request.user, topic.course):
            raise PermissionDenied(
                "You cannot access this discussion."
            )

        return topic

    def get_queryset(self):
        topic = self.get_topic()

        return ForumReply.objects.filter(
            topic=topic
        ).select_related("created_by")

    def perform_create(self, serializer):
        topic = self.get_topic()

        if topic.is_closed:
            raise PermissionDenied(
                "This discussion is closed."
            )

        serializer.save(
            topic=topic,
            created_by=self.request.user
        )


class ForumReplyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ForumReplySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ForumReply.objects.filter(
            topic__in=ForumTopic.objects.filter(
                course__in=Course.objects.all()
            )
        ).select_related("topic", "topic__course")

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)

        if not can_access_course(request.user, obj.topic.course):
            raise PermissionDenied(
                "You cannot access this reply."
            )

    def update(self, request, *args, **kwargs):
        reply = self.get_object()

        if (
            reply.created_by_id != request.user.id
            and request.user.role not in ["ADMIN", "TRAINER"]
        ):
            raise PermissionDenied("You cannot edit this reply.")

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        reply = self.get_object()

        if (
            reply.created_by_id != request.user.id
            and request.user.role not in ["ADMIN", "TRAINER"]
        ):
            raise PermissionDenied("You cannot delete this reply.")

        return super().destroy(request, *args, **kwargs)


class LiveClassListCreateView(generics.ListCreateAPIView):
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = LiveClass.objects.select_related(
            "course", "trainer"
        )

        if user.role == "ADMIN":
            return queryset

        if user.role == "TRAINER":
            return queryset.filter(course__trainer=user)

        if user.role == "STUDENT":
            enrolled_courses = Enrollment.objects.filter(
                student=user,
                status__in=["ACTIVE", "COMPLETED"]
            ).values_list("course_id", flat=True)

            return queryset.filter(
                course_id__in=enrolled_courses,
                is_cancelled=False
            )

        return LiveClass.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role not in ["ADMIN", "TRAINER"]:
            raise PermissionDenied(
                "Only trainers and administrators can schedule live classes."
            )

        course = get_object_or_404(
            Course,
            id=self.request.data.get("course")
        )

        if user.role == "TRAINER" and course.trainer_id != user.id:
            raise PermissionDenied(
                "You can schedule classes only for your own courses."
            )

        serializer.save(
            course=course,
            trainer=user
        )


class LiveClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return LiveClass.objects.all()

        if user.role == "TRAINER":
            return LiveClass.objects.filter(course__trainer=user)

        if user.role == "STUDENT":
            enrolled_courses = Enrollment.objects.filter(
                student=user,
                status__in=["ACTIVE", "COMPLETED"]
            ).values_list("course_id", flat=True)

            return LiveClass.objects.filter(
                course_id__in=enrolled_courses,
                is_cancelled=False
            )

        return LiveClass.objects.none()

    def update(self, request, *args, **kwargs):
        if request.user.role not in ["ADMIN", "TRAINER"]:
            raise PermissionDenied(
                "Only trainers and administrators can update live classes."
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role not in ["ADMIN", "TRAINER"]:
            raise PermissionDenied(
                "Only trainers and administrators can delete live classes."
            )

        return super().destroy(request, *args, **kwargs)
