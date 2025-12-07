# wallet/tests/test_apis.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from wallet.models import Wallet, Transaction

User = get_user_model()

class WalletAPITests(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='testpass123'
        )
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
    
    def test_get_wallet_balance(self):
        """Test GET /api/wallet/ returns wallet info"""
        # Create a wallet with some balance
        wallet = Wallet.objects.create(user=self.user, balance=Decimal('150.00'))
        
        response = self.client.get('/api/wallet/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], '150.00')  # Serializer returns string
        self.assertEqual(response.data['user'], self.user.id)
        print("✅ GET wallet balance test passed!")
    
    def test_deposit_via_api(self):
        """Test POST /api/wallet/deposit/ adds money"""
        response = self.client.post('/api/wallet/deposit/', {
            'amount': '75.00',
            'description': 'API test deposit'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        
        # Verify the balance was updated in database
        wallet = Wallet.objects.get(user=self.user)
        self.assertEqual(float(wallet.balance), 75.00)
        print("✅ API deposit test passed!")
    
    def test_deposit_invalid_amount(self):
        """Test deposit with invalid amount returns error"""
        response = self.client.post('/api/wallet/deposit/', {
            'amount': '-50.00',  # Negative amount
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        print("✅ Invalid deposit error handling test passed!")
    
    def test_get_transactions_via_api(self):
        """Test GET /api/wallet/transactions/ returns transaction history"""
        # Create a wallet and some transactions first
        wallet = Wallet.objects.create(user=self.user, balance=Decimal('100.00'))
        Transaction.objects.create(
            wallet=wallet,
            amount=Decimal('50.00'),
            transaction_type='deposit',
            description='Test transaction 1'
        )
        Transaction.objects.create(
            wallet=wallet,
            amount=Decimal('25.00'),
            transaction_type='withdrawal',
            description='Test transaction 2'
        )
        
        response = self.client.get('/api/wallet/transactions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return 2 transactions
        self.assertEqual(response.data[0]['amount'], '25.00')  # Most recent first
        self.assertEqual(response.data[1]['amount'], '50.00')
        print("✅ Get transactions API test passed!")
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access wallet API"""
        unauthenticated_client = APIClient()  # No authentication
        
        response = unauthenticated_client.get('/api/wallet/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✅ Unauthenticated access protection test passed!")

    # wallet/tests/test_apis.py - ADD THIS METHOD
    def test_debug_urls(self):
        """Debug: See all registered wallet URLs"""
        from django.urls import get_resolver
    
        def list_urls(patterns, prefix=''):
            urls = []
            for pattern in patterns:
                if hasattr(pattern, 'url_patterns'):
                # This is an include - recurse into it
                    urls.extend(list_urls(
                        pattern.url_patterns, 
                        prefix + str(pattern.pattern)
                    ))
                elif hasattr(pattern, 'pattern'):
                # This is a URL pattern
                    url_str = prefix + str(pattern.pattern)
                    if 'wallet' in url_str:
                        urls.append(url_str)
            return urls
    
        resolver = get_resolver()
        all_urls = list_urls(resolver.url_patterns)
    
        print("=== REGISTERED WALLET URLs ===")
        for url in sorted(all_urls):
            print(f"  {url}")
        print("==============================")