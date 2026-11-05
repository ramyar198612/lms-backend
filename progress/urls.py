from django.urls import path
from .views import (
    MarkLessonCompleteView,
    MyLearningProgressView,
    CourseProgressDetailView,
    TrainerCourseProgressView,
)

urlpatterns = [
    path(
        "complete/<int:lesson_id>/",
        MarkLessonCompleteView.as_view(),
        name="mark-lesson-complete"
    ),

    path(
        "my-progress/",
        MyLearningProgressView.as_view(),
        name="my-learning-progress"
    ),

    path(
        "course/<int:course_id>/",
        CourseProgressDetailView.as_view(),
        name="course-progress-detail"
    ),

    path(
        "reports/",
        TrainerCourseProgressView.as_view(),
        name="trainer-course-progress"
    ),
]