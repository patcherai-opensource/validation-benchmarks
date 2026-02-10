from django.contrib import admin
from django.urls import path
from .views import index, inventory, report

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('inventory/', inventory, name='inventory'),
    path('report/', report, name='report'),
]

handler404 = 'ssti_demo.views.handler404'
handler500 = 'ssti_demo.views.handler500'
