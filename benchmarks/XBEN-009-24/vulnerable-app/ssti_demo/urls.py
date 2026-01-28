from django.contrib import admin
from django.urls import path
from .views import index, preview, content_list, about, docs, search

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('preview/', preview, name='preview'),
    path('api/content/', content_list, name='content_list'),
    path('about/', about, name='about'),
    path('docs/', docs, name='docs'),
    path('search/', search, name='search'),
]
