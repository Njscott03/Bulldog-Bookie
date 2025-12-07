# wallet/services/allowance_service.py
from django.utils import timezone
from datetime import timedelta
from .wallet_service import WalletService

class AllowanceService:
    @staticmethod
    def setup_allowance(user, amount=100.00, frequency='weekly'):
        """Set up initial allowance for user"""
        from wallet.models import AllowanceConfig
        
        next_distribution = timezone.now() + timedelta(days=7)  # Default weekly
        
        allowance, created = AllowanceConfig.objects.get_or_create(
            user=user,
            defaults={
                'amount': amount,
                'frequency': frequency,
                'next_distribution': next_distribution,
            }
        )
        return allowance
    
    @staticmethod
    def distribute_allowance(user):
        """Distribute allowance if it's due"""
        try:
            allowance = user.allowance_config
            if (allowance.is_active and 
                timezone.now() >= allowance.next_distribution):
                
                # Add allowance to wallet
                WalletService.deposit(
                    user, 
                    allowance.amount, 
                    f"{allowance.get_frequency_display()} allowance"
                )
                
                # Update next distribution date
                if allowance.frequency == 'daily':
                    allowance.next_distribution = timezone.now() + timedelta(days=1)
                elif allowance.frequency == 'weekly':
                    allowance.next_distribution = timezone.now() + timedelta(weeks=1)
                elif allowance.frequency == 'monthly':
                    allowance.next_distribution = timezone.now() + timedelta(days=30)
                
                allowance.save()
                return True
        except:
            return False