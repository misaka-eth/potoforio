from bs4 import BeautifulSoup

from providers import BalanceProvider
from core.models import Asset, Wallet, Blockchain


class LitecoinblockexplorerClient(BalanceProvider):
    async def scan_wallet(self, wallet: Wallet):
        url = f"https://litecoinblockexplorer.net/xpub/{wallet.address}"
        response = await self._request('GET', url)
        response = await response.text()

        soup = BeautifulSoup(response, 'html.parser')

        balance: str = soup.find_all(class_='table')[0].find_all(class_='data')[2].text
        balance = float(balance.replace(' LTC', '')) * pow(10, 8)
        balance = str(int(balance))

        blockchain_ltc = Blockchain.objects.filter(name="Litecoin").last()
        asset_ltc = Asset.objects.filter(ticker='LTC').last()

        await self._update_balance(wallet=wallet, blockchain=blockchain_ltc, asset=asset_ltc, balance=str(balance))

    async def scan_all_wallet(self):
        wallets = Wallet.objects.filter()

        for wallet in wallets:
            if wallet.address.startswith('zpub') or wallet.address.startswith('Ltub'):
                await self.scan_wallet(wallet)
