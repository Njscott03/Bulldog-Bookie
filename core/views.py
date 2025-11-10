from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CustomUser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

def home(request):
    return HttpResponse("<h1>Welcome to Bulldog Bookie!</h1>")

def is_admin_user(user):
    return user.is_authenticated and user.is_admin

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_admin:
                return redirect('admin_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'core/login.html')

class StudentDashboardAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Welcome to the student dashboard!"})


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

