from potoforio.providers import BalanceProvider

from potoforio.core.models import Asset, Wallet, Blockchain


class BlackscoutBalanceProvider(BalanceProvider):
    API_URL = 'https://blockscout.com/xdai/mainnet/api'
    BLOCKCHAIN_NAME = 'Gnosis'

    async def scan_wallet(self, wallet: Wallet):
        params = {
            'module': 'account',
            'action': 'eth_get_balance',
            'address': wallet.address
        }
        response = await self._request('GET', self.API_URL, params=params)
        response = await response.json()

        blockchain = Blockchain.objects.filter(name=self.BLOCKCHAIN_NAME).last()
        asset = Asset.objects.filter(ticker='DAI').last()

        result = response.get('result')
        if result:
            balance = int(result, 16)

            await self._update_balance(wallet=wallet, blockchain=blockchain, asset=asset, balance=str(balance))

    def match_address(self, address: str):
        return len(address) == 42 and address.startswith('0x')
