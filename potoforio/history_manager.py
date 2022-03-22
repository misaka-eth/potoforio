import time
import logging
from threading import Thread
from core.models import Wallet, BalanceHistory
from core.serializers import WalletSerializer

LOGGER = logging.getLogger(__name__)


def history_manager():
    def manage():
        while True:
            # Wait for all data (wallet balances, prices, etc.) to update before start
            time.sleep(60)

            # Calculate total balance
            wallets = Wallet.objects.all()
            total_balance = 0
            for wallet in wallets:
                for assets_on_blockchains in WalletSerializer(wallet).data['assets_on_blockchains']:
                    balance = assets_on_blockchains.get('balance').get('balance')
                    decimals = assets_on_blockchains.get('asset_on_blockchain').get('asset').get('decimals')
                    last_price = assets_on_blockchains.get('asset_on_blockchain').get('asset').get('last_price')

                    current_balance = int(balance)/pow(10, decimals) * last_price
                    total_balance += current_balance

            # Format and save
            total_balance = float(f'{total_balance:.2f}')
            if total_balance != 0.0:
                LOGGER.debug(f"Update total balance to: {total_balance}")
                BalanceHistory.objects.create(balance=total_balance)
            else:
                LOGGER.debug("Total balance = 0. Skip")

            time.sleep(60 * 4)

    thread = Thread(target=manage)
    thread.start()
