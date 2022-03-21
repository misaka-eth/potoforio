import aiohttp
from providers import BalanceProvider

from core.models import Wallet, Blockchain, TokenOnBlockchain


class EthplorerClient(BalanceProvider):
    API_URL = 'https://api.ethplorer.io'

    def __init__(self, apikey="freekey"):
        super().__init__()
        self._api_key = apikey

    async def scan_wallet(self, wallet: Wallet):
        params = {
            'apiKey': self._api_key
        }
        url = f"{EthplorerClient.API_URL}/getAddressInfo/{wallet.address}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response = await response.json()

                blockchain_eth = Blockchain.objects.filter(name="Ethereum").last()
                eth_on_eth = TokenOnBlockchain.objects.filter(blockchain=blockchain_eth, token__ticker="ETH").last()
                eth_balance = response.get('ETH').get('rawBalance')

                await self._update_balance(
                    wallet=wallet,
                    blockchain=blockchain_eth,
                    token=eth_on_eth.token,
                    balance=eth_balance
                )

                tokens = response.get('tokens', [])
                for token in tokens:
                    address = token.get('tokenInfo').get('address')
                    balance = token.get("rawBalance")
                    ticker = "<UNKNOWN>"

                    token_on_eth = TokenOnBlockchain.objects.filter(blockchain=blockchain_eth, address=address).last()
                    if not token_on_eth:
                        self._logger.warning(f"Unknown token: {balance} {ticker} with address {address}")
                        continue

                    await self._update_balance(
                        wallet=wallet,
                        blockchain=blockchain_eth,
                        token=token_on_eth.token,
                        balance=balance
                    )

    async def scan_all_wallet(self):
        wallets = Wallet.objects.filter()

        for wallet in wallets:
            if len(wallet.address) == 42 and wallet.address.startswith('0x'):
                await self.scan_wallet(wallet)
