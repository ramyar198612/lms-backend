
from django.contrib import admin
from .models import ForumTopic, ForumReply, LiveClass


class ForumReplyInline(admin.TabularInline):
    model = ForumReply
    extra = 0


@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "course",
        "created_by",
        "is_closed",
        "created_at",
    )
    list_filter = ("is_closed", "created_at")
    search_fields = ("title", "description", "created_by__username")
    inlines = [ForumReplyInline]


@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "created_by", "created_at")
    search_fields = ("message", "created_by__username")


@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "course",
        "trainer",
        "scheduled_at",
        "is_cancelled",
    )
    list_filter = ("is_cancelled", "scheduled_at")
    search_fields = ("title", "course__title", "trainer__username")
