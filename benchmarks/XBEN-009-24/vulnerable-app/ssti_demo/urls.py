from django.contrib import admin
from django.urls import path
from .views import directory, index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('directory/', directory),
    path('', index),
]
