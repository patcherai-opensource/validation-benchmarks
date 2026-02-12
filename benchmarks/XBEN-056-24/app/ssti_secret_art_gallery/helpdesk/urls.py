from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='helpdesk_dashboard'),
    path('tickets/', views.ticket_list, name='helpdesk_ticket_list'),
    path('tickets/datatables/', views.datatables_ticket_list, name='helpdesk_datatables'),
    path('tickets/create/', views.create_ticket, name='helpdesk_create_ticket'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='helpdesk_ticket_detail'),
    path('tickets/<int:ticket_id>/update/', views.update_ticket, name='helpdesk_update_ticket'),
    path('tickets/report/', views.report_ticket, name='helpdesk_report_ticket'),
    path('submit/', views.public_create_ticket, name='helpdesk_public_create'),
    path('webhook/', views.webhook_log, name='helpdesk_webhook'),
]