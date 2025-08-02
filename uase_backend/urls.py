# In uase_backend/urls.py (your main project urls.py)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import custom error handling views
from core import views as core_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), # Include your app's URLs
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = core_views.custom_404
handler500 = core_views.custom_500
