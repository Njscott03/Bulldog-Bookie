# wallet/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Wallet, AllowanceConfig
from .services.allowance_service import AllowanceService

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """Automatically create wallet and allowance for new users"""
    if created:
        # Create wallet
        Wallet.objects.create(user=instance)
        
        # Set up default allowance
        AllowanceService.setup_allowance(instance)