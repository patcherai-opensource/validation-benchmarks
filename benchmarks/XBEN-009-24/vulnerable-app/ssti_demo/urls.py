from django.contrib import admin
from django.urls import path
from .views import index, ticket_create, public_ticket_ajax, admin_login, api_docs

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('public/ticket/', ticket_create, name='ticket_create'),
    path('public/ticket/ajax/ajax.php', public_ticket_ajax, name='public_ticket_ajax'),  # Mimics Dolibarr endpoint
    path('user/login/', admin_login, name='admin_login'),
    path('api/docs/', api_docs, name='api_docs'),
]
