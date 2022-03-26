from providers import BalanceProvider

from core.models import Asset, Wallet, Blockchain


class BeaconchainClient(BalanceProvider):
    API_URL = 'https://beaconcha.in/api/v1/'

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
            response_text = await response.text()
            response_text = response_text.replace("\n", '')
            self._logger.warning(f"Bad response with code: {response.status} | {response_text}")
            return

        response = await response.json()

        blockchain_eth2 = Blockchain.objects.filter(name="Ethereum Validator").last()
        asset_eth = Asset.objects.filter(ticker='ETH').last()
        balance = response.get('data').get('balance') * pow(10, 9)

        await self._update_balance(wallet=wallet, blockchain=blockchain_eth2, asset=asset_eth, balance=str(balance))

    def match_address(self, address: str):
        return len(address) == 98 and address.startswith('0x')
