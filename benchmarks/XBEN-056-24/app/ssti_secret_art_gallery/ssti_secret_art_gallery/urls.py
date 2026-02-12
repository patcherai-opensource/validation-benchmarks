"""
URL configuration for ssti_secret_art_gallery project.
"""

from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from accounts.views import gallery_view

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('', gallery_view, name='gallery'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
