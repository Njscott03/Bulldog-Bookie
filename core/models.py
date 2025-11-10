from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)  # instructors/bookies
    wallet_balance = models.DecimalField(default=1000.00, max_digits=10, decimal_places=2)

    def __str__(self):
        return self.username
