from django.urls import path

from .views import (
    AssignmentListCreateView,
    AssignmentDetailView,
    AssignmentSubmissionCreateView,
    MySubmissionsView,
    SubmissionReviewView,
)

urlpatterns = [
    path("", AssignmentListCreateView.as_view(), name="assignment-list-create"),
    path("<int:pk>/", AssignmentDetailView.as_view(), name="assignment-detail"),
    path("submit/", AssignmentSubmissionCreateView.as_view(), name="assignment-submit"),
    path("my-submissions/", MySubmissionsView.as_view(), name="my-submissions"),
    path("review/<int:pk>/", SubmissionReviewView.as_view(), name="submission-review"),
]