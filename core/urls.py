from django.urls import path
from . import views, api_views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # Public
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Student
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('wagers/', views.student_wagers_view, name='wagers'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/bookie/', views.admin_bookie_view, name='admin_bookie'),
    path('admin-dashboard/wagers/', views.admin_wagers_view, name='admin_wagers'),
    path('admin-dashboard/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin-dashboard/edit/<int:user_id>/', views.edit_user, name='edit_user'),

    # API
    path('api/auth/register/', api_views.RegisterAPI.as_view(), name='api_register'),
    path('api/auth/login/', api_views.LoginAPI.as_view(), name='api_login'),
    path('api/auth/refresh/', api_views.RefreshTokenAPI.as_view(), name='api_refresh'),
    path('api/admin/wagers/', api_views.AdminWagersAPI.as_view(), name='api_admin_wagers'),
]
