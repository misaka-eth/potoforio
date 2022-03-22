from providers import BalanceProvider
from bs4 import BeautifulSoup

from core.models import Wallet, Blockchain, AssetOnBlockchain


class EtherscanBalanceProvider(BalanceProvider):
    def __init__(self):
        super().__init__()
        self._unknown_assets = []

    async def scan_wallet(self, wallet: Wallet):
        url = f"https://etherscan.io/address/{wallet.address}"
        response = await self._request('GET', url)
        response = await response.text()
        soup = BeautifulSoup(response, 'html.parser')

        blockchain_eth = Blockchain.objects.filter(name="Ethereum").last()
        eth_on_eth = AssetOnBlockchain.objects.filter(blockchain=blockchain_eth, asset__ticker="ETH").last()

        balance = soup.find_all(class_='col-md-8')
        balance = float(balance[0].text.replace(' Ether', ''))
        balance = int(balance * pow(10, eth_on_eth.asset.decimals))

        await self._update_balance(
            wallet=wallet,
            blockchain=blockchain_eth,
            asset=eth_on_eth.asset,
            balance=str(balance)
        )

        erc20_assets = soup.find_all(class_="list-custom-ERC20")

        for erc20_asset in erc20_assets:
            href = erc20_asset.find('a').get('href')
            amount, ticker = erc20_asset.find(class_='list-amount').text.split()
            amount = amount.replace(',', "")
            asset_address = href.split("?")[0].split("/")[2]
            self._logger.debug(f"{wallet.address}: {amount}{ticker}")

            asset_on_eth = AssetOnBlockchain.objects.filter(address=asset_address).last()

            if not asset_on_eth:
                if asset_address not in self._unknown_assets:
                    self._unknown_assets.append(asset_address)
                    self._logger.warning(f"Unknown asset: {amount} {ticker} with address {asset_address}")
                continue

            balance = str(int(float(amount) * pow(10, asset_on_eth.asset.decimals)))

            await self._update_balance(
                wallet=wallet,
                blockchain=blockchain_eth,
                asset=asset_on_eth.asset,
                balance=balance
            )

    async def scan_all_wallet(self):
        wallets = Wallet.objects.filter()

        for wallet in wallets:
            if len(wallet.address) == 42 and wallet.address.startswith('0x'):
                await self.scan_wallet(wallet)
