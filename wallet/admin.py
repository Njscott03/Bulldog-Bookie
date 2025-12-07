# wallet/admin.py
from django.contrib import admin
from .models import Wallet, Transaction, AllowanceConfig

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at']  # Columns in list view
    list_filter = ['created_at']  # Filters on the right
    search_fields = ['user__username']  # Search by username
    readonly_fields = ['created_at']  # Can't edit these
    
    def get_queryset(self, request):
        # Optimize database queries
        return super().get_queryset(request).select_related('user')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'transaction_type', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    date_hierarchy = 'created_at'  # Date navigation
    
    def wallet_user(self, obj):
        return obj.wallet.user.username
    wallet_user.short_description = 'User'  # Custom column

@admin.register(AllowanceConfig)
class AllowanceConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'frequency', 'is_active']
    list_editable = ['amount', 'is_active']  # Edit directly in list view
    actions = ['enable_allowances', 'disable_allowances']
    
    def enable_allowances(self, request, queryset):
        queryset.update(is_active=True)
    enable_allowances.short_description = "Enable selected allowances"