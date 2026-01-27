"""
URL configuration for TaskFlow Scheduler project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from accounts.views import dashboard_view, task_detail_view, task_logs_view

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('', dashboard_view, name='dashboard'),
    path('tasks/', dashboard_view, name='tasks_list'),
    path('tasks/detail', task_detail_view, name='task_detail'),
    path('tasks/logs', task_logs_view, name='task_logs'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
