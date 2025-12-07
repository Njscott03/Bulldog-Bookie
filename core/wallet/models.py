# wallet/models.py
from django.db import models
from django.contrib.auth import get_user_model  # ✅ Correct way!
from django.core.validators import MinValueValidator
from decimal import Decimal

# Get the custom user model from your settings
User = get_user_model()

class Wallet(models.Model):
    user = models.OneToOneField(
        User,  # ✅ Now points to your custom user model
        on_delete=models.CASCADE, 
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Wallet - ${self.balance}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('bet_placed', 'Bet Placed'),
        ('bet_won', 'Bet Won'),
        ('bet_lost', 'Bet Lost'),
        ('allowance', 'Allowance'),
    ]
    
    wallet = models.ForeignKey(
        Wallet, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_type} - ${self.amount}"

class AllowanceConfig(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    user = models.OneToOneField(
        User,  # ✅ Use custom user model here too
        on_delete=models.CASCADE, 
        related_name='allowance_config'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='weekly')
    next_distribution = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Allowance - ${self.amount} {self.frequency}"