from django.urls import path

from .views import (
    CourseCategoryListView,
    CourseListView,
    CourseCreateView,
    CourseDetailView,
)

urlpatterns = [
    path("categories/", CourseCategoryListView.as_view(), name="course-categories"),
    path("", CourseListView.as_view(), name="course-list"),
    path("create/", CourseCreateView.as_view(), name="course-create"),
    path("<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
]