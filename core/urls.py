from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # HTML routes
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # JWT API routes
    path('api/auth/register/', views.RegisterAPI.as_view(), name='api_register'),
    path('api/auth/login/', views.LoginAPI.as_view(), name='api_login'),
    path('api/auth/refresh/', views.RefreshTokenAPI.as_view(), name='api_refresh'),
]
