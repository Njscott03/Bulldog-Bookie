# wallet/tests/test_services.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from wallet.services.wallet_service import WalletService
from wallet.models import Wallet, Transaction

User = get_user_model()

class WalletServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='serviceuser',
            email='service@example.com',
            password='testpass123'
        )
    
    def test_deposit_increases_balance(self):
        """Test that deposit increases wallet balance"""
        initial_balance = WalletService.get_user_wallet(self.user).balance
        
        wallet = WalletService.deposit(self.user, Decimal('100.00'), "Test deposit")
        
        self.assertEqual(wallet.balance, initial_balance + Decimal('100.00'))
        self.assertEqual(Transaction.objects.count(), 1)
        
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.transaction_type, 'deposit')
        self.assertEqual(transaction.amount, Decimal('100.00'))
        print("✅ Deposit service test passed!")
    

    def test_withdraw_decreases_balance(self):
        """Test that withdrawal decreases wallet balance"""  # ✅ Fixed docstring
    
    # First, deposit money so we have something to withdraw
        WalletService.deposit(self.user, Decimal('200.00'), "Setup for withdrawal test")
        initial_balance = WalletService.get_user_wallet(self.user).balance  # Should be 200.00
    
    # Withdraw some money
        wallet = WalletService.withdraw(self.user, Decimal('50.00'), "Test withdrawal")

    # Verify balance decreased correctly
        self.assertEqual(wallet.balance, initial_balance - Decimal('50.00'))  # 200 - 50 = 150
        self.assertEqual(Transaction.objects.count(), 2)  # Deposit + Withdrawal
    
    # Verify withdrawal transaction details
        withdrawal_transaction = Transaction.objects.filter(transaction_type='withdrawal').first()
        self.assertEqual(withdrawal_transaction.transaction_type, 'withdrawal')  # ✅ Fixed spelling
        self.assertEqual(withdrawal_transaction.amount, Decimal('50.00'))  # ✅ Correct amount
        print("✅ Withdrawal service test passed!")  # ✅ Fixed message
    
    def test_insufficient_funds_raises_error(self):
        """Test that withdrawal fails with insufficient funds"""
        with self.assertRaises(ValueError) as context:
            WalletService.withdraw(self.user, Decimal('100.00'), "Should fail")
        
        self.assertIn("Insufficient funds", str(context.exception))
        print("✅ Insufficient funds test passed!")