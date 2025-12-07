# wallet/services/__init__.py
from .wallet_service import WalletService

__all__ = ['WalletService']
# wallet/__init__.py (to connect signals)
default_app_config = 'wallet.apps.WalletConfig'