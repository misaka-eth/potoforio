from providers import BalanceProvider

from core.models import Asset, Wallet, Blockchain


class BeaconchainClient(BalanceProvider):
    API_URL = 'https://beaconcha.in/api/v1/'

    def __init__(self, apikey="freekey"):
        super().__init__()
        self._api_key = apikey

    async def scan_wallet(self, wallet: Wallet):
        params = {
            'apiKey': self._api_key
        }
        url = f"{BeaconchainClient.API_URL}/validator/{wallet.address}"
        response = await self._request('GET', url, params=params)
        response = await response.json()

        blockchain_eth2 = Blockchain.objects.filter(name="Ethereum Validator").last()
        asset_eth = Asset.objects.filter(ticker='ETH').last()
        balance = response.get('data').get('balance') * pow(10, 9)

        await self._update_balance(wallet=wallet, blockchain=blockchain_eth2, asset=asset_eth, balance=str(balance))

    def match_address(self, address: str):
        return len(address) == 98 and address.startswith('0x')

