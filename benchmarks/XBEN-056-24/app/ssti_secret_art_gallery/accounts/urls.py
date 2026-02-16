from django.urls import path
from .views import (
    register_step1, register_step2, register_step3,
    login_view, home_view, preferences_view, logout_view,
    content_list_view, content_create_view, content_edit_view,
    content_preview_view, content_delete_view,
)

urlpatterns = [
    path('register/step1/', register_step1, name='register_step1'),
    path('register/step2/', register_step2, name='register_step2'),
    path('register/step3/', register_step3, name='register_step3'),
    path('login/', login_view, name='login'),
    path('home/', home_view, name='home'),
    path('preferences/', preferences_view, name='preferences'),
    path('logout/', logout_view, name='logout'),
    path('pages/', content_list_view, name='content_list'),
    path('pages/create/', content_create_view, name='content_create'),
    path('pages/<int:page_id>/edit/', content_edit_view, name='content_edit'),
    path('pages/<int:page_id>/preview/', content_preview_view, name='content_preview'),
    path('pages/<int:page_id>/delete/', content_delete_view, name='content_delete'),
]
