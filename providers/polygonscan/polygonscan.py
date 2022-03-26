from providers import BalanceProvider
from bs4 import BeautifulSoup

from core.models import Wallet, Blockchain, AssetOnBlockchain


class PolygonScan(BalanceProvider):
    def __init__(self, configuration: dict):
        super().__init__(configuration)
        self._unknown_assets = []

    async def scan_wallet(self, wallet: Wallet):
        url = f"https://polygonscan.com/address/{wallet.address}"
        response = await self._request('GET', url)
        response = await response.text()

        soup = BeautifulSoup(response, 'html.parser')

        erc20_assets = soup.find_all(class_="list-custom-ERC-20")
        for erc20_asset in erc20_assets:
            href = erc20_asset.find('a').get('href')
            amount, ticker = erc20_asset.find(class_='list-amount').text.split()
            asset_address = href.split("?")[0].split("/")[2]
            self._logger.debug(f"{wallet.address}: {amount}{ticker}")

            blockchain_polygon = Blockchain.objects.filter(name="Polygon").last()
            asset_on_polygon = AssetOnBlockchain.objects.filter(address=asset_address).last()

            if not asset_on_polygon:
                if asset_address not in self._unknown_assets:
                    self._unknown_assets.append(asset_address)
                    self._logger.warning(f"Unknown asset: {amount} {ticker} with address {asset_address}")
                continue

            balance = str(int(float(amount) * pow(10, asset_on_polygon.asset.decimals)))

            await self._update_balance(
                wallet=wallet,
                blockchain=blockchain_polygon,
                asset=asset_on_polygon.asset,
                balance=balance
            )

    def match_address(self, address: str):
        return len(address) == 42 and address.startswith('0x')
