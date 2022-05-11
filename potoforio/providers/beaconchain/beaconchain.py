from potoforio.providers import BalanceProvider, ProviderInvalidResponse

from potoforio.core.models import Asset, Wallet, Blockchain
from potoforio.helpers.parsers import normalize_power


class BeaconchainClient(BalanceProvider):
    API_URL = 'https://beaconcha.in/api/v1/'
    BLOCKCHAIN_NAME = "Ethereum Validator"

    @staticmethod
    def get_default_configuration():
        configuration = BalanceProvider.get_default_configuration()  # TODO: super don't work for some reason
        configuration['api_key'] = 'freekey'
        return configuration

    async def scan_wallet(self, wallet: Wallet):
        params = {
            'apiKey': self._configuration['api_key']
        }
        url = f"{BeaconchainClient.API_URL}/validator/{wallet.address}"
        response = await self._request('GET', url, params=params)

        # Check if response is valid
        if response.status != 200 or response.content_type != 'application/json':
            raise ProviderInvalidResponse(f"Bad response with code: {response.status}")

        response = await response.json()

        blockchain_eth2 = Blockchain.objects.filter(name=self.BLOCKCHAIN_NAME).last()
        asset_eth = Asset.objects.filter(ticker='ETH').last()

        balance = response.get('data').get('balance')

        # Process parsed string to correct balance
        balance = normalize_power(balance, 9, normal_power=asset_eth.decimals)

        await self._update_balance(wallet=wallet, blockchain=blockchain_eth2, asset=asset_eth, balance=str(balance))

    def match_address(self, address: str):
        return len(address) == 98 and address.startswith('0x')
