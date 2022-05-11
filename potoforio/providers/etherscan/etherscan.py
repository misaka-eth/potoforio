from potoforio.providers import BalanceProvider
from bs4 import BeautifulSoup

from potoforio.core.models import Wallet, Blockchain, Asset, AssetOnBlockchain
from potoforio.helpers.parsers import parse_float


class EtherscanBalanceProvider(BalanceProvider):
    BLOCKCHAIN_NAME = 'Ethereum'

    def __init__(self, configuration: dict):
        super().__init__(configuration)

        self._unknown_assets = []

    async def scan_wallet(self, wallet: Wallet):
        url = f"https://etherscan.io/address/{wallet.address}"
        response = await self._request('GET', url)
        response = await response.text()
        soup = BeautifulSoup(response, 'html.parser')

        blockchain_eth = Blockchain.objects.filter(name=self.BLOCKCHAIN_NAME).last()
        asset_eth = Asset.objects.filter(ticker="ETH").last()

        balance = soup.find_all(class_='col-md-8')
        balance = balance[0].text.replace(' Ether', '').replace(',', "")
        # Process parsed string to correct balance
        balance = parse_float(balance, normal_power=asset_eth.decimals)

        await self._update_balance(
            wallet=wallet,
            blockchain=blockchain_eth,
            asset=asset_eth,
            balance=str(balance)
        )

        erc20_assets = soup.find_all(class_="list-custom-ERC20")

        for erc20_asset in erc20_assets:
            href = erc20_asset.find('a').get('href')
            amount, ticker = erc20_asset.find(class_='list-amount').text.split()
            amount = amount.replace(',', "")
            asset_address = href.split("?")[0].split("/")[2]

            asset_on_eth = AssetOnBlockchain.objects.filter(address=asset_address).last()

            if not asset_on_eth:
                if asset_address not in self._unknown_assets:
                    self._unknown_assets.append(asset_address)
                    self._logger.warning(f"Unknown asset: {amount} {ticker} with address {asset_address}")
                continue

            # Process parsed string to correct balance
            balance = parse_float(amount, normal_power=asset_on_eth.asset.decimals)

            await self._update_balance(
                wallet=wallet,
                blockchain=blockchain_eth,
                asset=asset_on_eth.asset,
                balance=balance
            )

    def match_address(self, address: str):
        return len(address) == 42 and address.startswith('0x')
