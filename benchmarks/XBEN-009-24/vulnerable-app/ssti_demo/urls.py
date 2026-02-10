from django.contrib import admin
from django.urls import path
from .views import sort_items, index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sort/', sort_items, name='sort_items'),
    path('', index, name='index'),
]
