# wallet/services/wallet_service.py
from django.db import transaction as db_transaction
from decimal import Decimal
from wallet.models import Wallet, Transaction

class WalletService:
    @staticmethod
    def get_user_wallet(user):
        """Get or create wallet for user - handle anonymous users"""
        if user.is_anonymous:
            raise ValueError("Authentication required to access wallet")
        
        wallet, created = Wallet.objects.get_or_create(user=user)
        return wallet
    
    @staticmethod
    @db_transaction.atomic
    def deposit(user, amount, description="Deposit"):
        """Add funds to user's wallet"""
        wallet = WalletService.get_user_wallet(user)
        
        # Convert everything to float for arithmetic, then back to Decimal
        current_balance = float(wallet.balance)
        deposit_amount = float(amount)
        
        # Validate amount
        if deposit_amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        new_balance = current_balance + deposit_amount
        wallet.balance = Decimal(str(new_balance))
        wallet.save()
        
        # Create transaction record
        Transaction.objects.create(
            wallet=wallet,
            amount=Decimal(str(deposit_amount)),
            transaction_type='deposit',
            description=description
        )
        return wallet
    
    @staticmethod
    @db_transaction.atomic
    def withdraw(user, amount, description="Withdrawal"):
        """Withdraw funds from user's wallet"""
        wallet = WalletService.get_user_wallet(user)
        
        # Convert everything to float for arithmetic
        current_balance = float(wallet.balance)
        withdraw_amount = float(amount)
        
        # Validate amount
        if withdraw_amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if current_balance < withdraw_amount:
            raise ValueError("Insufficient funds")
        
        new_balance = current_balance - withdraw_amount
        wallet.balance = Decimal(str(new_balance))
        wallet.save()
        
        Transaction.objects.create(
            wallet=wallet,
            amount=Decimal(str(withdraw_amount)),
            transaction_type='withdrawal',
            description=description
        )
        return wallet
    
    # Add to wallet/services/wallet_service.py
    @staticmethod
    @db_transaction.atomic
    def place_bet(user, amount, bet_description):
        """Place a bet - hold funds"""
        return WalletService.withdraw(user, amount, f"Bet: {bet_description}")

    @staticmethod  
    @db_transaction.atomic
    def settle_bet(user, amount, won=True, bet_description=""):
        """Settle a bet - add winnings or confirm loss"""
        if won:
            # Add winnings back (original bet + winnings)
            WalletService.deposit(user, amount, f"Bet won: {bet_description}")
        # If lost, funds were already deducted when bet was placed