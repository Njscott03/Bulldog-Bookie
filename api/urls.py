from django.urls import path
from .views import RegisterView, LoginView, RefreshTokenView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api_register'),
    path('login/', LoginView.as_view(), name='api_login'),
    path('refresh/', RefreshTokenView.as_view(), name='api_refresh'),
]
