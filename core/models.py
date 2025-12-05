# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    # keep whatever fields you already have
    is_admin = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00)

    def __str__(self):
        return self.username

class Wager(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('WON', 'Won'),
        ('LOST', 'Lost'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wagers')
    game = models.CharField(max_length=255)              # e.g. "MSU vs TAMU"
    line = models.CharField(max_length=64, blank=True)  # e.g. "-7.5"
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payout = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    placed_at = models.DateTimeField(default=timezone.now)
    settled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-placed_at']

    def __str__(self):
        return f"{self.user.username} - {self.game} - {self.amount} ({self.status})"

    @property
    def profit(self):
        # positive payout - amount: if payout is what was returned
        return (self.payout - self.amount)
