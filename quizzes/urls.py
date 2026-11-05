from django.urls import path

from .views import (
    QuizListCreateView,
    QuizDetailView,
    QuestionCreateView,
    QuizStartView,
    QuizSubmitView,
    MyQuizResultsView,
    QuizResultDetailView,
)

urlpatterns = [
    path("", QuizListCreateView.as_view(), name="quiz-list-create"),
    path("<int:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("questions/create/", QuestionCreateView.as_view(), name="question-create"),
    path("<int:pk>/start/", QuizStartView.as_view(), name="quiz-start"),
    path("attempts/<int:pk>/submit/", QuizSubmitView.as_view(), name="quiz-submit"),
    path("results/", MyQuizResultsView.as_view(), name="quiz-results"),
    path("results/<int:pk>/", QuizResultDetailView.as_view(), name="quiz-result-detail"),
]