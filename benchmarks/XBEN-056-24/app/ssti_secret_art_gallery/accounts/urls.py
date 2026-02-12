from django.urls import path
from .views import (
    register_step1, register_step2, register_step3,
    login_view, home_view, preferences_view, logout_view,
    page_list_view, page_create_view, page_edit_view, page_detail_view,
)

urlpatterns = [
    path('register/step1/', register_step1, name='register_step1'),
    path('register/step2/', register_step2, name='register_step2'),
    path('register/step3/', register_step3, name='register_step3'),
    path('login/', login_view, name='login'),
    path('home/', home_view, name='home'),
    path('preferences/', preferences_view, name='preferences'),
    path('logout/', logout_view, name='logout'),
    path('pages/', page_list_view, name='page_list'),
    path('pages/new/', page_create_view, name='page_create'),
    path('pages/<slug:slug>/edit/', page_edit_view, name='page_edit'),
    path('pages/<slug:slug>/', page_detail_view, name='page_detail'),
]
