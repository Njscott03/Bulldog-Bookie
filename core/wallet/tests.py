# wallet/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal

# Use absolute imports - no dots!
from wallet.models import Wallet, Transaction

User = get_user_model()

class WalletModelTests(TestCase):
    def setUp(self):
        """Set up test data that will be available in every test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_wallet_creation(self):
        """Test that we can create a wallet"""
        wallet = Wallet.objects.create(user=self.user, balance=Decimal('100.00'))
        self.assertEqual(wallet.balance, Decimal('100.00'))
        self.assertEqual(wallet.user, self.user)
        print("✅ Wallet creation test passed!")
    
    def test_wallet_string_representation(self):
        """Test the string representation of Wallet"""
        wallet = Wallet.objects.create(user=self.user, balance=Decimal('100.00'))
        self.assertEqual(str(wallet), "testuser's Wallet - $100.00")
        print("✅ Wallet string representation test passed!")


class TransactionModelTests(TestCase):
    def setUp(self):
        """Set up test data for transaction tests"""
        self.user = User.objects.create_user(
            username='transactionuser',
            email='transaction@example.com',
            password='testpass123'
        )
        self.wallet = Wallet.objects.create(user=self.user, balance=Decimal('200.00'))
    
    def test_transaction_creation(self):
        """Test creating a transaction"""
        transaction = Transaction.objects.create(
            wallet=self.wallet,
            amount=Decimal('50.00'),
            transaction_type='deposit',
            description='Test deposit'
        )
        
        self.assertEqual(transaction.amount, Decimal('50.00'))
        self.assertEqual(transaction.transaction_type, 'deposit')
        self.assertEqual(transaction.wallet, self.wallet)
        print("✅ Transaction creation test passed!")
    
    def test_transaction_string_representation(self):
        """Test the string representation of Transaction"""
        transaction = Transaction.objects.create(
            wallet=self.wallet,
            amount=Decimal('25.00'),
            transaction_type='withdrawal',
            description='Test withdrawal'
        )
        
        self.assertEqual(str(transaction), "withdrawal - $25.00")
        print("✅ Transaction string representation test passed!")


# Run a simple test first to make sure imports work
class SimpleImportTest(TestCase):
    def test_basic_imports(self):
        """Test that all imports work correctly"""
        user = User.objects.create_user(
            username='importtestuser',
            email='import@example.com',
            password='testpass123'
        )
        
        # Test Wallet import and creation
        wallet = Wallet.objects.create(user=user, balance=Decimal('50.00'))
        self.assertIsNotNone(wallet)
        
        # Test Transaction import and creation
        transaction = Transaction.objects.create(
            wallet=wallet,
            amount=Decimal('10.00'),
            transaction_type='deposit',
            description='Import test'
        )
        self.assertIsNotNone(transaction)
        
        print("✅ All imports working correctly!")