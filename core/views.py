from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, F
from .models import CustomUser, Wager
from wallet.services import WalletService

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

from django.shortcuts import render
from django.core.cache import cache
from datetime import datetime

def nba_odds(request):
    """Simple view to display NBA odds"""
    
    # Try to get from cache first
    games = cache.get('nba_odds')
    
    if games is None:
        # If not in cache, fetch fresh data
        import requests
        from django.conf import settings
        from datetime import timedelta
        
        API_KEY = settings.ODDS_API_KEY
        base_url = "https://api.odds-api.io/v3"
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        events_response = requests.get(
            f"{base_url}/events",
            params={
                'apiKey': API_KEY,
                'sport': 'basketball',
                'league': 'usa-nba',
                'from': today.isoformat() + 'Z',
                'to': tomorrow.isoformat() + 'Z'
            }
        )
        
        games = []
        if events_response.status_code == 200:
            events = events_response.json()
            for event in events:
                game_data = {
                    'id': event.get('id'),
                    'home': event.get('home'),
                    'away': event.get('away'),
                    'date': event.get('date'),
                    'odds': []
                }
                
                odds_response = requests.get(
                    f"{base_url}/odds",
                    params={
                        'apiKey': API_KEY,
                        'eventId': event.get('id'),
                        'bookmakers': 'DraftKings,FanDuel,Bet365'
                    }
                )
                
                if odds_response.status_code == 200:
                    odds_data = odds_response.json()
                    bookmakers = odds_data.get('bookmakers', {})
                    
                    for bookmaker_name, markets in bookmakers.items():
                        for market in markets:
                            if market.get('name') == 'ML':
                                odds = market.get('odds', {})
                                
                                if isinstance(odds, list):
                                    home_odds = next((o.get('price') for o in odds if o.get('name') == game_data['home']), 'N/A')
                                    away_odds = next((o.get('price') for o in odds if o.get('name') == game_data['away']), 'N/A')
                                else:
                                    home_odds = odds.get('home', 'N/A')
                                    away_odds = odds.get('away', 'N/A')
                                
                                game_data['odds'].append({
                                    'bookmaker': bookmaker_name,
                                    'home_odds': home_odds,
                                    'away_odds': away_odds
                                })
                
                games.append(game_data)
            
            # Cache for 5 minutes
            cache.set('nba_odds', games, 300)
    
    context = {
        'games': games,
        'today': datetime.now().strftime('%B %d, %Y')
    }
    
    return render(request, 'core/student_wagers.html', context)

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
    print("DEBUG: wallet_view is running!")
    user = request.user
    
    try:
        
        # Get wallet from WalletService
        wallet = WalletService.get_user_wallet(user)
        print(f"DEBUG: Using WalletService. Balance: {wallet.balance}")
        
        # Get recent transactions
        transactions = wallet.transactions.all().order_by('-created_at')[:10]
        
        return render(request, "core/wallet.html", {
            "user": user,
            "wallet": wallet,  # Pass the wallet object
            "wallet_balance": wallet.balance,  # Use wallet.balance, not user.wallet_balance
            "transactions": transactions,
            "wagers": user.wagers.all().order_by('-placed_at')[:10],
        })
        
    except Exception as e:
        # Fallback to simple system if wallet not ready
        print(f"DEBUG: WalletService failed. Using fallback. Error: {e}")
        
        return render(request, "core/wallet.html", {
            "user": user,
            "wallet_balance": user.wallet_balance,  # Old field as fallback
            "wagers": user.wagers.all().order_by('-placed_at')[:10],
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
