import logging
import aiohttp

from core.models import Asset, AssetPriceHistory, AssetOnBlockchain, WalletWithAssetOnBlockchain, Blockchain, Wallet, \
    WalletHistoryWithAssetOnBlockchain


class ProviderConnectionError(Exception):
    pass


class Provider:
    def __init__(self, configuration: dict):
        self._configuration = configuration
        self._logger = logging.getLogger(self.__class__.__name__)

    async def _request(self, method: str, url: str, **kwargs):
        self._logger.debug(f">> Request {method} {url} {kwargs}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, url, **kwargs) as response:
                    self._logger.debug(f"<< Response {await response.read()}")
                    return response
            except aiohttp.ClientConnectorError as error:
                raise ProviderConnectionError from error

    @staticmethod
    def get_default_configuration():
        """
        Called on first register event.
        Must return dict of default parameters
        """
        return {
            "timeout": 60
        }

    def get_configuration(self, key: str):
        return self._configuration.get(key)

    async def run(self):
        raise NotImplementedError


class PriceProvider(Provider):
    async def _update_price(self, ticker: str, price: float):
        assets = Asset.objects.filter(ticker=ticker).all()
        if not assets:
            self._logger.warning(f"Can't find asset {ticker}.")
            return
        for asset in assets:
            log_prefix = f"Update price for asset: {asset} -"
            last_price = AssetPriceHistory.objects.filter(asset=asset).order_by('timestamp').last()
            if not last_price or last_price.price != price:
                if last_price:
                    price_difference = price - last_price.price
                    price_difference_str = f"{'+' if price_difference > 0 else ''}{price_difference:.2f}"
                else:
                    price_difference_str = "~"
                self._logger.debug(f"{log_prefix} New price: {price} ({price_difference_str})")
                AssetPriceHistory.objects.create(asset=asset, price=price)
            else:
                self._logger.debug(f"{log_prefix} Skip update: price doesn't change")

    async def scan(self):
        raise NotImplementedError

    async def run(self):
        return await self.scan()


class BalanceProvider(Provider):
    async def _update_balance(self, wallet: Wallet, asset: Asset, blockchain: Blockchain, balance: str):
        asset_on_blockchain = AssetOnBlockchain.objects.filter(blockchain=blockchain, asset=asset).last()
        if not asset_on_blockchain:
            self._logger.warning(f"Asset {asset} not found on blockchain {blockchain}")
            return

        wallet_with_asset_on_blockchain, created = WalletWithAssetOnBlockchain.objects.get_or_create(
            asset_on_blockchain=asset_on_blockchain,
            wallet=wallet
        )

        if created:
            self._logger.info(f"Found {wallet_with_asset_on_blockchain}")

        last_record = WalletHistoryWithAssetOnBlockchain.objects.filter(
            wallet_with_asset_on_blockchain=wallet_with_asset_on_blockchain
        ).last()

        if last_record and last_record.balance == balance:
            self._logger.debug(f"Balance not changed for {wallet_with_asset_on_blockchain}")
            return

        WalletHistoryWithAssetOnBlockchain.objects.create(
            wallet_with_asset_on_blockchain=wallet_with_asset_on_blockchain,
            balance=balance
        )
        last_record_balance = "0" if not last_record else last_record.balance
        self._logger.info(f"Balance for {wallet_with_asset_on_blockchain} updated. {last_record_balance}->{balance}")

        return

    def match_address(self, address: str):
        raise NotImplementedError

    async def scan_wallet(self, wallet: Wallet):
        raise NotImplementedError

    async def scan_all_wallet(self):
        wallets = Wallet.objects.all()

        for wallet in wallets:
            if self.match_address(wallet.address):
                await self.scan_wallet(wallet)

    async def run(self):
        return await self.scan_all_wallet()
