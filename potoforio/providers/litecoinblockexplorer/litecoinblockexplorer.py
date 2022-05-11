from bs4 import BeautifulSoup

from potoforio.providers import BalanceProvider
from potoforio.core.models import Asset, Wallet, Blockchain
from potoforio.helpers.parsers import parse_float


class LitecoinblockexplorerClient(BalanceProvider):
    BLOCKCHAIN_NAME = 'Litecoin'

    async def scan_wallet(self, wallet: Wallet):
        url = f"https://litecoinblockexplorer.net/xpub/{wallet.address}"
        response = await self._request('GET', url)
        response = await response.text()

        blockchain_ltc = Blockchain.objects.filter(name=self.BLOCKCHAIN_NAME).last()
        asset_ltc = Asset.objects.filter(ticker='LTC').last()

        soup = BeautifulSoup(response, 'html.parser')

        balance: str = soup.find_all(class_='table')[0].find_all(class_='data')[2].text
        balance = balance.replace(' LTC', '')
        # Process parsed string to correct balance
        balance = parse_float(balance, normal_power=asset_ltc.decimals)

        await self._update_balance(wallet=wallet, blockchain=blockchain_ltc, asset=asset_ltc, balance=str(balance))

    def match_address(self, address: str):
        return address.startswith('zpub') or address.startswith('Ltub')
