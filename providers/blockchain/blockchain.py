import aiohttp

from providers import BalanceProvider
from core.models import Wallet, Blockchain, TokenOnBlockchain


class BlockchainClient(BalanceProvider):
    API_URL = 'https://blockchain.info'

    async def scan_wallet(self, wallet: Wallet):
        url = f"{BlockchainClient.API_URL}/balance?active={wallet.address}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response = await response.json()

                blockchain_btc = Blockchain.objects.filter(name="Bitcoin").last()
                btc_on_btc = TokenOnBlockchain.objects.filter(blockchain=blockchain_btc, token__ticker="BTC").last()

                balance = str(response.get(wallet.address).get('final_balance'))

                await self._update_balance(
                    wallet=wallet,
                    blockchain=blockchain_btc,
                    token=btc_on_btc.token,
                    balance=balance
                )

    async def scan_all_wallet(self):
        wallets = Wallet.objects.filter()

        for wallet in wallets:
            if len(wallet.address) == 34 and wallet.address.startswith('3'):
                await self.scan_wallet(wallet)
