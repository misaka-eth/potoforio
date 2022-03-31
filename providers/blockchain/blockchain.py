from providers import BalanceProvider

from core.models import Wallet, Blockchain, Asset


class BlockchainClient(BalanceProvider):
    API_URL = 'https://blockchain.info'
    BLOCKCHAIN_NAME = "Bitcoin"

    async def scan_wallet(self, wallet: Wallet):
        url = f"{BlockchainClient.API_URL}/balance?active={wallet.address}"
        response = await self._request('GET', url)
        response = await response.json()

        blockchain_btc = Blockchain.objects.filter(name=self.BLOCKCHAIN_NAME).last()
        asset_btc = Asset.objects.filter(ticker="BTC").last()

        balance = str(response.get(wallet.address).get('final_balance'))

        await self._update_balance(
            wallet=wallet,
            blockchain=blockchain_btc,
            asset=asset_btc,
            balance=balance
        )

    def match_address(self, address: str):
        return len(address) == 34 and address.startswith('3')
