from django.urls import path
from .views import (
    announcements_list,
    announcement_file_view,
    announcement_pdf_page,
    pdf_viewer,
)

urlpatterns = [
    # Страница объявлений
    path("announcements/", announcements_list, name="announcements-list"),
    path(
        "announcements/file/<int:pk>/",
        announcement_file_view,
        name="announcement-file-view",
    ),
    path(
        "announcements/pdfpage/<int:pk>/",
        announcement_pdf_page,
        name="announcement-pdf-page",
    ),
    path("announcements/pdfjs/<int:pk>/", pdf_viewer, name="announcement-pdfjs-viewer"),
]
