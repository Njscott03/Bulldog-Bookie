# wallet/tests/test_integration.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from wallet.services import WalletService

class WalletIntegrationTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass'
        )
    
    def test_wallet_creation(self):
        """Test wallet is created for user"""
        wallet = WalletService.get_user_wallet(self.user)
        self.assertIsNotNone(wallet)
        self.assertEqual(wallet.user, self.user)
    
    def test_deposit_works(self):
        """Test deposit functionality"""
        wallet = WalletService.deposit(self.user, 100.00, "Test deposit")
        self.assertEqual(float(wallet.balance), 100.00)
    
    def test_withdrawal_works(self):
        """Test withdrawal functionality"""
        # First deposit
        WalletService.deposit(self.user, 200.00, "Initial deposit")
        
        # Then withdraw
        wallet = WalletService.withdraw(self.user, 50.00, "Test withdrawal")
        self.assertEqual(float(wallet.balance), 150.00)
    
    def test_transaction_history(self):
        """Test transaction recording"""
        # Make multiple transactions
        WalletService.deposit(self.user, 100.00, "Deposit 1")
        WalletService.withdraw(self.user, 30.00, "Withdrawal 1")
        WalletService.deposit(self.user, 50.00, "Deposit 2")
        
        # Get wallet to check transactions
        wallet = WalletService.get_user_wallet(self.user)
        transactions = wallet.transactions.all()
        
        self.assertEqual(transactions.count(), 3)
        self.assertEqual(float(wallet.balance), 120.00)
    
    def test_insufficient_funds(self):
        """Test that withdrawal fails with insufficient funds"""
        with self.assertRaises(ValueError) as context:
            WalletService.withdraw(self.user, 100.00, "Withdrawal without funds")
        
        self.assertIn('Insufficient funds', str(context.exception))