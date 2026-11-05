from .permissions import IsStudent, IsTrainer, IsAdministrator
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    StudentRegistrationSerializer,
    TrainerRegistrationSerializer,
)
from rest_framework.views import APIView

class StudentRegistrationView(generics.CreateAPIView):
    serializer_class = StudentRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class TrainerRegistrationView(generics.CreateAPIView):
    serializer_class = TrainerRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        })

class StudentDashboardView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        return Response({
            "message": "Welcome to the Student Dashboard!",
            "username": request.user.username,
            "role": request.user.role,
        })


class TrainerDashboardView(APIView):
    permission_classes = [IsTrainer]

    def get(self, request):
        return Response({
            "message": "Welcome to the Trainer Dashboard!",
            "username": request.user.username,
            "role": request.user.role,
        })
class AdminDashboardView(APIView):
    permission_classes = [IsAdministrator]

    def get(self, request):
        return Response({
            "message": "Welcome to the Administrator Dashboard!",
            "username": request.user.username,
            "role": request.user.role,
        })