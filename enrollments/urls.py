from django.urls import path

from .views import (
    CourseEnrollmentView,
    MyEnrollmentsView,
)

urlpatterns = [
    path("enroll/", CourseEnrollmentView.as_view(), name="course-enroll"),
    path("my-courses/", MyEnrollmentsView.as_view(), name="my-enrollments"),
]