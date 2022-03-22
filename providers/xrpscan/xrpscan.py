from providers import BalanceProvider

from core.models import Asset, Wallet, Blockchain


class XrpscanClient(BalanceProvider):
    API_URL = 'https://api.xrpscan.com/api/v1'

    async def scan_wallet(self, wallet: Wallet):
        url = f"{XrpscanClient.API_URL}/account/{wallet.address}"
        response = await self._request('GET', url)
        response = await response.json()

        balance = float(response.get('xrpBalance')) * pow(10, 6)
        balance = str(int(balance))

        blockchain_ripple = Blockchain.objects.filter(name="Ripple").last()
        asset_xrp = Asset.objects.filter(ticker='XRP').last()

        await self._update_balance(wallet=wallet, blockchain=blockchain_ripple, asset=asset_xrp, balance=str(balance))

    async def scan_all_wallet(self):
        wallets = Wallet.objects.filter()

        for wallet in wallets:
            if wallet.address.startswith('r'):
                await self.scan_wallet(wallet)
