from django.contrib import admin
from django.urls import path
from .views import render_page, index, about, contact

urlpatterns = [
    path('admin/', admin.site.urls),
    path('page/', render_page),
    path('about/', about),
    path('contact/', contact),
    path('', index),
]

handler404 = 'ssti_demo.views.custom_404'
handler500 = 'ssti_demo.views.custom_500'
