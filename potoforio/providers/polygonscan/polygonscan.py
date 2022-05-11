from potoforio.providers import BalanceProvider
from bs4 import BeautifulSoup

from potoforio.core.models import Wallet, Blockchain, AssetOnBlockchain
from potoforio.helpers.parsers import parse_float, normalize_power


class PolygonScan(BalanceProvider):
    BLOCKCHAIN_NAME = 'Polygon'

    def __init__(self, configuration: dict):
        super().__init__(configuration)
        self._unknown_assets = []

    async def scan_wallet(self, wallet: Wallet):
        blockchain_polygon = Blockchain.objects.filter(name=self.BLOCKCHAIN_NAME).last()

        url = f'https://polygonscan.com/address/{wallet.address}'
        response = await self._request('GET', url)
        response = await response.text()

        soup = BeautifulSoup(response, 'html.parser')

        matic_on_polygon = AssetOnBlockchain.objects.filter(address='0x0000000000000000000000000000000000001010').last()

        balance = soup.find_all(class_='col-md-8')
        balance = balance[0].text.replace(' MATIC ', '').replace(',', '')

        # Process parsed string to correct balance
        balance = parse_float(balance, normal_power=matic_on_polygon.asset.decimals)

        # Save balance only if it's non-zero
        if balance:
            await self._update_balance(
                wallet=wallet,
                blockchain=blockchain_polygon,
                asset=matic_on_polygon.asset,
                balance=balance
            )

        erc20_assets = soup.find_all(class_='list-custom-ERC-20')
        for erc20_asset in erc20_assets:
            href = erc20_asset.find('a').get('href')
            balance, ticker = erc20_asset.find(class_='list-amount').text.replace(',', '').split()
            asset_address = href.split("?")[0].split("/")[2]

            # Skip MATIC token, due to incorrect representation in list
            if asset_address == '0x0000000000000000000000000000000000001010':
                continue

            self._logger.debug(f'Found asset {wallet.address}: {balance}{ticker}')

            asset_on_polygon = AssetOnBlockchain.objects.filter(address=asset_address).last()

            if not asset_on_polygon:
                # Show record in log only one time per session
                if asset_address not in self._unknown_assets:
                    self._unknown_assets.append(asset_address)
                    self._logger.warning(f'Unknown asset: {balance} {ticker} with address {asset_address}')
                continue

            # Process parsed string to correct balance
            balance = parse_float(balance, normal_power=asset_on_polygon.asset.decimals)

            await self._update_balance(
                wallet=wallet,
                blockchain=blockchain_polygon,
                asset=asset_on_polygon.asset,
                balance=str(balance)
            )

    def match_address(self, address: str):
        return len(address) == 42 and address.startswith('0x')
