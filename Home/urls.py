from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("school.urls")),
    path('student/', include("student.urls")),
    path('teachers/', include('teacher.urls')),
    path('academics/', include('academics.urls')),
    path('authentication/', include("home_auth.urls")),
]

# Serve uploaded student photos while developing
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
