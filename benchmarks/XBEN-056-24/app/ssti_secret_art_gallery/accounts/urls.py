from django.urls import path
from .views import register_step1, register_step2, register_step3
from .views import login_view, home_view, preferences_view, logout_view
from .views import dashboard_view, team_directory_view, api_departments_view, api_projects_view, reports_view

urlpatterns = [
    path('register/step1/', register_step1, name='register_step1'),
    path('register/step2/', register_step2, name='register_step2'),
    path('register/step3/', register_step3, name='register_step3'),
    path('login/', login_view, name='login'),
    path('home/', home_view, name='home'),
    path('preferences/', preferences_view, name='preferences'),
    path('logout/', logout_view, name='logout'),
    path('team/', team_directory_view, name='team_directory'),
    path('api/departments/', api_departments_view, name='api_departments'),
    path('api/projects/', api_projects_view, name='api_projects'),
    path('reports/', reports_view, name='reports'),
]
