
from django.urls import path

from .views import (
    NotificationListView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
    AnnouncementListCreateView,
    AnnouncementDetailView,
)

urlpatterns = [
    path(
        "",
        NotificationListView.as_view(),
        name="notification-list"
    ),

    path(
        "<int:notification_id>/read/",
        MarkNotificationReadView.as_view(),
        name="notification-read"
    ),

    path(
        "read-all/",
        MarkAllNotificationsReadView.as_view(),
        name="notification-read-all"
    ),

    path(
        "announcements/",
        AnnouncementListCreateView.as_view(),
        name="announcement-list-create"
    ),

    path(
        "announcements/<int:pk>/",
        AnnouncementDetailView.as_view(),
        name="announcement-detail"
    ),
]
