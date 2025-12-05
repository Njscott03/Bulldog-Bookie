from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, F
from .models import CustomUser, Wager

# ----------------------------
# Helper Functions
# ----------------------------
def is_admin_user(user):
    return user.is_authenticated and (user.is_admin or user.is_staff or user.is_superuser)

# ----------------------------
# PUBLIC VIEWS
# ----------------------------
def home(request):
    return render(request, "core/home.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST.get("email", "")
        password = request.POST["password"]

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "core/register.html")

        CustomUser.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")

    return render(request, "core/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if is_admin_user(user):
                return redirect("admin_dashboard")
            return redirect("student_dashboard")

        messages.error(request, "Invalid credentials.")

    return render(request, "core/login.html")

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")

# ----------------------------
# STUDENT VIEWS
# ----------------------------
@login_required
def student_dashboard(request):
    wagers = request.user.wagers.all().order_by('-placed_at')
    total_wagered = wagers.aggregate(total=Sum("amount"))["total"] or 0

    return render(request, "core/student_dashboard.html", {
        "user": request.user,
        "wagers": wagers[:10],
        "total_wagered": total_wagered,
    })

@login_required
def student_wagers_view(request):
    wagers = request.user.wagers.all().order_by('-placed_at')
    total_wagered = wagers.aggregate(total=Sum("amount"))["total"] or 0

    return render(request, "core/student_wagers.html", {
        "wagers": wagers,
        "total_wagered": total_wagered,
    })

# ----------------------------
# WALLET VIEW
# ----------------------------
@login_required
def wallet_view(request):
    user = request.user
    wallet_balance = user.wallet_balance
    wagers = user.wagers.all().order_by('-placed_at')[:10]

    return render(request, "core/wallet.html", {
        "user": user,
        "wallet_balance": wallet_balance,
        "wagers": wagers,
    })

# ----------------------------
# ADMIN VIEWS
# ----------------------------
@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):
    users = CustomUser.objects.all()
    total_users = users.count()
    total_wallets = users.aggregate(total=Sum("wallet_balance"))["total"] or 0
    total_wagered = Wager.objects.aggregate(total=Sum("amount"))["total"] or 0
    bookie_profit = Wager.objects.aggregate(profit=Sum(F("payout") - F("amount")))["profit"] or 0

    return render(request, "core/admin_dashboard.html", {
        "users": users,
        "total_users": total_users,
        "total_wallets": total_wallets,
        "total_wagered": total_wagered,
        "bookie_profit": bookie_profit,
    })

@login_required
@user_passes_test(is_admin_user)
def admin_bookie_view(request):
    qs = Wager.objects.filter(settled_at__isnull=False)

    by_day = {}
    for w in qs:
        day = w.settled_at.date().isoformat()
        if day not in by_day:
            by_day[day] = {"intake": 0, "payout": 0, "profit": 0}
        by_day[day]["intake"] += float(w.amount)
        by_day[day]["payout"] += float(w.payout)
        by_day[day]["profit"] += float(w.payout - w.amount)

    rows = sorted(by_day.items(), reverse=True)

    return render(request, "core/admin_bookie.html", {"rows": rows})

@login_required
@user_passes_test(is_admin_user)
def admin_wagers_view(request):
    qs = Wager.objects.select_related("user").all()

    username = request.GET.get("username")
    status = request.GET.get("status")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if username:
        qs = qs.filter(user__username__icontains=username)
    if status:
        qs = qs.filter(status__iexact=status)
    if date_from:
        qs = qs.filter(placed_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(placed_at__date__lte=date_to)

    return render(request, "core/admin_wagers.html", {
        "wagers": qs[:100],
        "filters": {
            "username": username or "",
            "status": status or "",
            "date_from": date_from or "",
            "date_to": date_to or "",
        },
    })

# ----------------------------
# ADMIN USER MANAGEMENT
# ----------------------------
@login_required
@user_passes_test(is_admin_user)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.success(request, "User deleted.")
    return redirect("admin_dashboard")

@login_required
@user_passes_test(is_admin_user)
def edit_user(request, user_id):
    user_obj = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        user_obj.email = request.POST.get("email", user_obj.email)
        wallet_balance = request.POST.get("wallet_balance")
        if wallet_balance:
            user_obj.wallet_balance = float(wallet_balance)
        user_obj.save()
        messages.success(request, "User updated.")
        return redirect("admin_dashboard")

    return render(request, "core/edit_user.html", {"user_obj": user_obj})
