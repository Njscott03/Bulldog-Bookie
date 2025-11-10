from django.urls import path
from . import views
from .views import StudentDashboardAPI

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin-dashboard/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('', views.home, name='home'),
    path('api/student-dashboard/', StudentDashboardAPI.as_view(), name='api_student_dashboard'),

]
