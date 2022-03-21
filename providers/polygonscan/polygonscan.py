from providers import BalanceProvider
from bs4 import BeautifulSoup

from core.models import Wallet, Blockchain, TokenOnBlockchain


class PolygonScan(BalanceProvider):
    def __init__(self):
        super().__init__()
        self._unknown_tokens = []

    async def scan_wallet(self, wallet: Wallet):
        url = f"https://polygonscan.com/address/{wallet.address}"
        response = await self._request('GET', url)
        response = await response.text()

        soup = BeautifulSoup(response, 'html.parser')

        erc20_tokens = soup.find_all(class_="list-custom-ERC-20")
        for erc20_token in erc20_tokens:
            href = erc20_token.find('a').get('href')
            amount, ticker = erc20_token.find(class_='list-amount').text.split()
            token_address = href.split("?")[0].split("/")[2]
            self._logger.debug(f"{wallet.address}: {amount}{ticker}")

            blockchain_polygon = Blockchain.objects.filter(name="Polygon").last()
            token_on_polygon = TokenOnBlockchain.objects.filter(address=token_address).last()

            if not token_on_polygon:
                if token_address not in self._unknown_tokens:
                    self._unknown_tokens.append(token_address)
                    self._logger.warning(f"Unknown token: {amount} {ticker} with address {token_address}")
                continue

            balance = str(int(float(amount) * pow(10, token_on_polygon.token.decimals)))

            await self._update_balance(
                wallet=wallet,
                blockchain=blockchain_polygon,
                token=token_on_polygon.token,
                balance=balance
            )

    async def scan_all_wallet(self):
        wallets = Wallet.objects.filter()

        for wallet in wallets:
            if len(wallet.address) == 42 and wallet.address.startswith('0x'):
                await self.scan_wallet(wallet)
