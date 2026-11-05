
from django.urls import path

from .views import (
    MyCertificatesView,
    IssueCertificateView,
    CertificateVerificationView,
    AllCertificatesView,
    CoursePerformanceReportView,
    StudentPerformanceReportView,
)

urlpatterns = [

    # Student certificates
    path(
        "my-certificates/",
        MyCertificatesView.as_view(),
        name="my-certificates"
    ),

    # Issue certificate
    path(
        "issue/",
        IssueCertificateView.as_view(),
        name="issue-certificate"
    ),

    # Verify certificate
    path(
        "verify/<uuid:certificate_number>/",
        CertificateVerificationView.as_view(),
        name="verify-certificate"
    ),

    # All certificates
    path(
        "all/",
        AllCertificatesView.as_view(),
        name="all-certificates"
    ),

    # Reports
    path(
        "reports/courses/",
        CoursePerformanceReportView.as_view(),
        name="course-performance-report"
    ),

    path(
        "reports/students/",
        StudentPerformanceReportView.as_view(),
        name="student-performance-report"
    ),
]
