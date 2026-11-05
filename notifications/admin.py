
from django.contrib import admin
from .models import Notification, Announcement


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
