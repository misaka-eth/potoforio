from potoforio.providers import BalanceProvider

from potoforio.core.models import Asset, Wallet, Blockchain
from potoforio.helpers.parsers import parse_float


class XrpscanClient(BalanceProvider):
    API_URL = 'https://api.xrpscan.com/api/v1'

    async def scan_wallet(self, wallet: Wallet):
        url = f"{XrpscanClient.API_URL}/account/{wallet.address}"
        response = await self._request('GET', url)
        response = await response.json()

        blockchain_ripple = Blockchain.objects.filter(name="Ripple").last()
        asset_xrp = Asset.objects.filter(ticker='XRP').last()

        balance = str(response.get('xrpBalance'))
        # Process parsed string to correct balance
        balance = parse_float(balance, normal_power=asset_xrp.decimals)

        await self._update_balance(wallet=wallet, blockchain=blockchain_ripple, asset=asset_xrp, balance=str(balance))

    def match_address(self, address: str):
        return address.startswith('r')
