from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import CustomUserSerializer


# -------------------- HTML Views --------------------

def home(request):
    return HttpResponse("<h1>Welcome to Bulldog Bookie!</h1>")


def is_admin_user(user):
    return user.is_authenticated and user.is_admin


def register_view(request):
    """Render an HTML registration form."""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST.get('email', '')
        password = request.POST['password']
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')
    return render(request, 'core/register.html')


def login_view(request):
    """Render an HTML login form."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Determine where to redirect based on admin status
            if getattr(user, "is_admin", False) or getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
                return redirect('admin_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'core/login.html')



@login_required
def logout_view(request):
    """Logout and redirect to login page."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def student_dashboard(request):
    return render(request, 'core/student_dashboard.html', {'user': request.user})


@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):
    users = CustomUser.objects.all()
    return render(request, 'core/admin_dashboard.html', {'users': users})


@login_required
@user_passes_test(is_admin_user)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if user.is_admin:
        messages.error(request, "Cannot delete another admin.")
    else:
        user.delete()
        messages.success(request, "User deleted successfully.")
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin_user)
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.email = request.POST.get('email', user.email)
        user.wallet_balance = request.POST.get('wallet_balance', user.wallet_balance)
        user.save()
        messages.success(request, "User updated successfully.")
        return redirect('admin_dashboard')
    return render(request, 'core/edit_user.html', {'user_obj': user})


# -------------------- JWT API Views --------------------

class RegisterAPI(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"username": user.username, "email": user.email},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class RefreshTokenAPI(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Missing refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            return Response({"access": new_access_token})
        except Exception:
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
