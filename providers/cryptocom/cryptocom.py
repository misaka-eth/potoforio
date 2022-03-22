from providers import BalanceProvider

from core.models import Asset, Wallet, Blockchain


class CryptocomClient(BalanceProvider):
    API_URL = 'https://crypto.org/explorer/api/v1'

    async def scan_wallet(self, wallet: Wallet):
        url = f"{CryptocomClient.API_URL}/accounts/{wallet.address}"
        response = await self._request('GET', url)
        response = await response.json()

        blockchain_cryptocom = Blockchain.objects.filter(name="Crypto.com").last()
        asset_cro = Asset.objects.filter(ticker='CRO').last()

        balance = str(int(float(response.get('result').get('totalBalance')[0].get('amount'))))
        await self._update_balance(
            wallet=wallet,
            blockchain=blockchain_cryptocom,
            asset=asset_cro,
            balance=balance
        )

    async def scan_all_wallet(self):
        wallets = Wallet.objects.filter()

        for wallet in wallets:
            if wallet.address.startswith('cro1'):
                await self.scan_wallet(wallet)
