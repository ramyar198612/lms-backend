from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Course, CourseCategory
from .serializers import CourseSerializer, CourseCategorySerializer


class CourseCategoryListView(generics.ListAPIView):
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer
    permission_classes = [permissions.AllowAny]


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]


class CourseCreateView(generics.CreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role not in ["TRAINER", "ADMIN"]:
            raise PermissionDenied("Only trainers and administrators can create courses.")

        serializer.save(trainer=self.request.user)

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]
    def get_queryset(self):
         user = self.request.user

         if not user.is_authenticated:
             return Course.objects.filter(is_published=True)

         if user.role == "ADMIN":
             return Course.objects.all()

         if user.role == "TRAINER":
          return Course.objects.filter(trainer=user)

         return Course.objects.filter(is_published=True)
    

    def get_object(self):
        course = super().get_object()
        user = self.request.user

        if self.request.method == "GET":
            return course

        if user.role == "ADMIN":
            return course

        if user.role == "TRAINER" and course.trainer_id == user.id:
            return course

        raise PermissionDenied("You cannot access this course.")
