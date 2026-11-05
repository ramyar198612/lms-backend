
from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "student",
        "course",
        "certificate_number",
        "issued_by",
        "issued_at",
    )

    search_fields = (
        "student__username",
        "course__title",
        "certificate_number",
    )

    list_filter = ("issued_at",)
    readonly_fields = ("certificate_number", "issued_at")
