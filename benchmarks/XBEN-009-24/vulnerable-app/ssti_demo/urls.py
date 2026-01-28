from django.contrib import admin
from django.urls import path
from .views import index, page_view, api_pages, api_layouts, docs, health, robots

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('page/<str:page_name>/', page_view, name='page_view'),
    path('api/pages/', api_pages, name='api_pages'),
    path('api/layouts/', api_layouts, name='api_layouts'),
    path('docs/', docs, name='docs'),
    path('health/', health, name='health'),
    path('robots.txt', robots, name='robots'),
]
