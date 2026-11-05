from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    message = "Only students can access this feature."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "STUDENT"
        )


class IsTrainer(BasePermission):
    message = "Only trainers can access this feature."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "TRAINER"
        )


class IsAdministrator(BasePermission):
    message = "Only administrators can access this feature."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )