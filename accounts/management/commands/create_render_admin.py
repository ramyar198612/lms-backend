import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the initial Render administrator account"

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            raise CommandError("Admin username and password environment variables are required.")

        User = get_user_model()

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            user.set_password(password)
        else:
            user.email = email or user.email
            user.role = "ADMIN"
            user.is_staff = True
            user.is_superuser = True

        user.save()

        self.stdout.write(
            self.style.SUCCESS(f"Render admin account ready: {username}")
        )