
from rest_framework import serializers
from .models import Notification, Announcement


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = [
            "id",
            "recipient",
            "title",
            "message",
            "notification_type",
            "created_at",
        ]


class AnnouncementSerializer(serializers.ModelSerializer):

    course_title = serializers.CharField(
        source="course.title",
        read_only=True
    )

    trainer_name = serializers.CharField(
        source="created_by.username",
        read_only=True
    )

    class Meta:
        model = Announcement
        fields = [
            "id",
            "course",
            "course_title",
            "created_by",
            "trainer_name",
            "title",
            "message",
            "is_published",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]
