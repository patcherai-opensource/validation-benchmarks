from django.contrib import admin
from django.urls import path
from .views import index, employees, departments, reports, api_employees, health

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('employees/', employees),
    path('departments/', departments),
    path('reports/', reports),
    path('api/employees/', api_employees),
    path('health/', health),
]
