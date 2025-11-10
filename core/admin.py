from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('is_admin', 'wallet_balance',)}),
    )
    list_display = ('username', 'email', 'is_admin', 'wallet_balance')
    list_filter = ('is_admin',)
