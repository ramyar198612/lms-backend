
from django.urls import path

from .views import (
    ForumTopicListCreateView,
    ForumTopicDetailView,
    ForumReplyListCreateView,
    ForumReplyDetailView,
    LiveClassListCreateView,
    LiveClassDetailView,
)

urlpatterns = [
    # Discussion topics
    path(
        "topics/",
        ForumTopicListCreateView.as_view(),
        name="forum-topic-list"
    ),

    path(
        "topics/<int:pk>/",
        ForumTopicDetailView.as_view(),
        name="forum-topic-detail"
    ),

    # Discussion replies
    path(
        "topics/<int:topic_id>/replies/",
        ForumReplyListCreateView.as_view(),
        name="forum-reply-list-create"
    ),

    path(
        "replies/<int:pk>/",
        ForumReplyDetailView.as_view(),
        name="forum-reply-detail"
    ),

    # Live classes
    path(
        "live-classes/",
        LiveClassListCreateView.as_view(),
        name="live-class-list-create"
    ),

    path(
        "live-classes/<int:pk>/",
        LiveClassDetailView.as_view(),
        name="live-class-detail"
    ),
]
