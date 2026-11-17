
from django.contrib import admin

from .models import Notification, Announcement
from enrollments.models import Enrollment


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recipient",
        "title",
        "notification_type",
        "is_read",
        "created_at",
    )

    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("recipient__username", "title", "message")


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "course",
        "created_by",
        "is_published",
        "created_at",
    )

    list_filter = ("is_published", "created_at")
    search_fields = ("title", "course__title", "message")

    def save_model(self, request, obj, form, change):
        was_published = False

        if change:
            previous = Announcement.objects.get(pk=obj.pk)
            was_published = previous.is_published

        super().save_model(request, obj, form, change)

        should_notify = (
            obj.is_published and not was_published
        )

        if should_notify:
            student_ids = Enrollment.objects.filter(
                course=obj.course,
                status__in=["ACTIVE", "COMPLETED"]
            ).values_list(
                "student_id", flat=True
            ).distinct()

            notifications = [
                Notification(
                    recipient_id=student_id,
                    title=obj.title,
                    message=obj.message,
                    notification_type=(
                        Notification.NotificationType.ANNOUNCEMENT
                    )
                )
                for student_id in student_ids
            ]

            Notification.objects.bulk_create(notifications)
