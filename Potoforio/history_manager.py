import time
from threading import Thread
from core.models import Wallet, BalanceHistory
from core.serializers import WalletSerializer


def history_manager():
    def manage():
        while True:
            # Wait for all data (wallet balances, prices, etc.) to update before start
            time.sleep(60)

            # Calculate total balance
            wallets = Wallet.objects.all()
            total_balance = 0
            for wallet in wallets:
                for tokens_on_blockchains in WalletSerializer(wallet).data['tokens_on_blockchains']:
                    balance = tokens_on_blockchains.get('balance').get('balance')
                    decimals = tokens_on_blockchains.get('token_on_blockchain').get('token').get('decimals')
                    last_price = tokens_on_blockchains.get('token_on_blockchain').get('token').get('last_price')

                    current_balance = int(balance)/pow(10, decimals) * last_price
                    total_balance += current_balance

            # Format and save
            total_balance = float(f'{total_balance:.2f}')
            BalanceHistory.objects.create(balance=total_balance)

    thread = Thread(target=manage)
    thread.start()
