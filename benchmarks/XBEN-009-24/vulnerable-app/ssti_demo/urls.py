from django.contrib import admin
from django.urls import path
from .views import view_document, index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', view_document, name='view_document'),
    path('', index),
]
