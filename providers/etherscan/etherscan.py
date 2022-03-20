from providers import BalanceProvider
from bs4 import BeautifulSoup

from core.models import Wallet, Blockchain, TokenOnBlockchain


class EtherscanBalanceProvider(BalanceProvider):
    async def scan_wallet(self, wallet: Wallet):
        url = f"https://etherscan.io/address/{wallet.address}"
        response = await self._request('GET', url)
        response = await response.text()
        soup = BeautifulSoup(response, 'html.parser')

        blockchain_eth = Blockchain.objects.filter(name="Ethereum").last()
        eth_on_eth = TokenOnBlockchain.objects.filter(blockchain=blockchain_eth, token__ticker="ETH").last()

        balance = soup.find_all(class_='col-md-8')
        balance = float(balance[0].text.replace(' Ether', ''))
        balance = int(balance * pow(10, eth_on_eth.token.decimals))

        await self._update_balance(
            wallet=wallet,
            blockchain=blockchain_eth,
            token=eth_on_eth.token,
            balance=str(balance)
        )

        erc20_tokens = soup.find_all(class_="list-custom-ERC20")

        for erc20_token in erc20_tokens:
            href = erc20_token.find('a').get('href')
            amount, ticker = erc20_token.find(class_='list-amount').text.split()
            amount = amount.replace(',', "")
            token_address = href.split("?")[0].split("/")[2]
            self._logger.debug(f"{wallet.address}: {amount}{ticker}")

            token_on_eth = TokenOnBlockchain.objects.filter(address=token_address).last()
            if not token_on_eth:
                self._logger.warning(f"Unknown token: {amount} {ticker} with address {token_address}")
                continue

            balance = str(int(float(amount) * pow(10, token_on_eth.token.decimals)))

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
