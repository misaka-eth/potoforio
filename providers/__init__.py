import logging
import aiohttp

from core.models import Asset, AssetPriceHistory, AssetOnBlockchain, WalletWithAssetOnBlockchain, Blockchain, Wallet, \
    WalletHistoryWithAssetOnBlockchain


class Provider:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    async def _request(self, method, url, **kwargs):
        self._logger.debug(f">> Request {method} {url} {kwargs}")

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                self._logger.debug(f"<< Response {await response.read()}")

                return response


class PriceProvider(Provider):
    async def _update_price(self, ticker, price):

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
            self._logger.debug(f"Balance not changed")
            return

        WalletHistoryWithAssetOnBlockchain.objects.create(
            wallet_with_asset_on_blockchain=wallet_with_asset_on_blockchain,
            balance=str(balance)
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
