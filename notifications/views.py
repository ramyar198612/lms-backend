
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError

from courses.models import Course
from enrollments.models import Enrollment
from .models import Notification, Announcement
from .serializers import NotificationSerializer, AnnouncementSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        )


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user
        )

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return Response({
            "message": "Notification marked as read.",
            "is_read": True
        })


class MarkAllNotificationsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({
            "message": "All notifications marked as read."
        })


def send_announcement_notifications(announcement):
    student_ids = Enrollment.objects.filter(
        course=announcement.course,
        status__in=["ACTIVE", "COMPLETED"]
    ).values_list("student_id", flat=True).distinct()

    notifications = [
        Notification(
            recipient_id=student_id,
            title=announcement.title,
            message=announcement.message,
            notification_type=Notification.NotificationType.ANNOUNCEMENT
        )
        for student_id in student_ids
    ]

    Notification.objects.bulk_create(notifications)

class AnnouncementListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return Announcement.objects.all().select_related(
                "course", "created_by"
            )

        if user.role == "TRAINER":
            return Announcement.objects.filter(
                course__trainer=user
            ).select_related("course", "created_by")

        if user.role == "STUDENT":
            enrolled_course_ids = Enrollment.objects.filter(
                student=user,
                status__in=["ACTIVE", "COMPLETED"]
            ).values_list("course_id", flat=True)

            return Announcement.objects.filter(
                course_id__in=enrolled_course_ids,
                is_published=True
            ).select_related("course", "created_by")

        raise PermissionDenied("You do not have permission.")

    
def perform_create(self, serializer):
    user = self.request.user
    course_id = self.request.data.get("course")

    if user.role not in ["ADMIN", "TRAINER"]:
        raise PermissionDenied(
            "Only trainers and administrators can create announcements."
        )

    course = get_object_or_404(Course, id=course_id)

    if user.role == "TRAINER" and course.trainer_id != user.id:
        raise PermissionDenied(
            "You can only announce in your own courses."
        )

    announcement = serializer.save(
        course=course,
        created_by=user
    )

    if announcement.is_published:
        send_announcement_notifications(announcement)


class AnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return Announcement.objects.all()

        if user.role == "TRAINER":
            return Announcement.objects.filter(
                course__trainer=user
            )

        if user.role == "STUDENT":
            enrolled_course_ids = Enrollment.objects.filter(
                student=user,
                status__in=["ACTIVE", "COMPLETED"]
            ).values_list("course_id", flat=True)

            return Announcement.objects.filter(
                course_id__in=enrolled_course_ids,
                is_published=True
            )

        return Announcement.objects.none()

   
def update(self, request, *args, **kwargs):
    if request.user.role not in ["ADMIN", "TRAINER"]:
        raise PermissionDenied(
            "Only trainers and administrators can update announcements."
        )

    if "course" in request.data:
        raise ValidationError(
            "An announcement cannot be moved to another course."
        )

    return super().update(request, *args, **kwargs)


def perform_update(self, serializer):
    announcement = self.get_object()
    was_published = announcement.is_published

    updated_announcement = serializer.save()

    if not was_published and updated_announcement.is_published:
        send_announcement_notifications(updated_announcement)


    def destroy(self, request, *args, **kwargs):
        if request.user.role not in ["ADMIN", "TRAINER"]:
            raise PermissionDenied(
                "Only trainers and administrators can delete announcements."
            )

        return super().destroy(request, *args, **kwargs)
