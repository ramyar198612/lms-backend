
from django.urls import path

from .views import (
    StudentRegistrationView,
    TrainerRegistrationView,
    UserProfileView,
    StudentDashboardView,
    TrainerDashboardView,
    AdminDashboardView,
)

urlpatterns = [
    path(
        "register/student/",
        StudentRegistrationView.as_view(),
        name="student-register",
    ),
    path(
        "register/trainer/",
        TrainerRegistrationView.as_view(),
        name="trainer-register",
    ),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("student/dashboard/", StudentDashboardView.as_view(), name="student-dashboard"),
    path("trainer/dashboard/", TrainerDashboardView.as_view(), name="trainer-dashboard"),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
]
