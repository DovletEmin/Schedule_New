from django.contrib import admin
from django.urls import path, include
from timetable.views import timetable_grid
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # Frontend
    path("", timetable_grid, name="timetable_grid"),
    path("", include("timetable.urls")),
    path('chaining/', include('smart_selects.urls')),

    # API
    # path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # path(
    #     "api/docs/",
    #     SpectacularSwaggerView.as_view(url_name="schema"),
    #     name="swagger-ui",
    # ),
    # path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Для раздачи media-файлов (PDF и др.) в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
