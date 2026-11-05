
from rest_framework import serializers
from .models import ForumTopic, ForumReply, LiveClass


class ForumReplySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.username",
        read_only=True
    )

    class Meta:
        model = ForumReply
        fields = [
            "id",
            "topic",
            "created_by",
            "created_by_name",
            "message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "topic",
            "created_by",
            "created_at",
            "updated_at",
        ]


class ForumTopicSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.username",
        read_only=True
    )
    course_title = serializers.CharField(
        source="course.title",
        read_only=True
    )
    replies = ForumReplySerializer(many=True, read_only=True)

    class Meta:
        model = ForumTopic
        fields = [
            "id",
            "course",
            "course_title",
            "created_by",
            "created_by_name",
            "title",
            "description",
            "is_closed",
            "replies",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]


class LiveClassSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source="course.title",
        read_only=True
    )
    trainer_name = serializers.CharField(
        source="trainer.username",
        read_only=True
    )

    class Meta:
        model = LiveClass
        fields = [
            "id",
            "course",
            "course_title",
            "trainer",
            "trainer_name",
            "title",
            "description",
            "meeting_link",
            "scheduled_at",
            "duration_minutes",
            "is_cancelled",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "trainer",
            "created_at",
            "updated_at",
        ]
