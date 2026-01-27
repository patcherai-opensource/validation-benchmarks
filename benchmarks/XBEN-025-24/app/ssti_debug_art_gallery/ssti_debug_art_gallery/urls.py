"""
URL configuration for filedock_webdav project.
FileDock - WebDAV File Browser
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from accounts.views import browser_view

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('browse/', browser_view, name='browser'),
    path('', browser_view),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
