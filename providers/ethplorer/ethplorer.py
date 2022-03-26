import aiohttp
from providers import BalanceProvider

from core.models import Wallet, Blockchain, AssetOnBlockchain, Asset


class EthplorerClient(BalanceProvider):
    API_URL = 'https://api.ethplorer.io'

    @staticmethod
    def get_default_configuration():
        configuration = super().get_default_configuration()
        configuration['api_key'] = 'freekey'
        return configuration

    async def scan_wallet(self, wallet: Wallet):
        params = {
            'apiKey': self._configuration['api_key']
        }
        url = f"{EthplorerClient.API_URL}/getAddressInfo/{wallet.address}"
        response = await self._request('GET', url, params=params)
        response = await response.json()

        blockchain_eth = Blockchain.objects.filter(name="Ethereum").last()
        asset_eth = Asset.objects.filter(ticker="ETH").last()
        eth_balance = response.get('ETH').get('rawBalance')

        await self._update_balance(
            wallet=wallet,
            blockchain=blockchain_eth,
            asset=asset_eth,
            balance=eth_balance
        )

        assets = response.get('tokens', [])
        for asset in assets:
            address = asset.get('tokenInfo').get('address')
            balance = asset.get("rawBalance")
            ticker = "<UNKNOWN>"

            asset_on_eth = AssetOnBlockchain.objects.filter(blockchain=blockchain_eth, address=address).last()
            if not asset_on_eth:
                self._logger.warning(f"Unknown asset: {balance} {ticker} with address {address}")
                continue

            await self._update_balance(
                wallet=wallet,
                blockchain=blockchain_eth,
                asset=asset_on_eth.asset,
                balance=balance
            )

    def match_address(self, address: str):
        return len(address) == 42 and address.startswith('0x')
