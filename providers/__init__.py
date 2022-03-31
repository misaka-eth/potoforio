import logging
import aiohttp

from core.models import Asset, AssetPriceHistory, AssetOnBlockchain, WalletWithAssetOnBlockchain, Blockchain, Wallet, \
    WalletHistoryWithAssetOnBlockchain, NFT, NFTCategory


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
    BLOCKCHAIN_NAME = ""

    def __init__(self, configuration: dict):
        super().__init__(configuration)
        self._all_assets = []

    async def _update_balance(self, wallet: Wallet, asset: Asset, blockchain: Blockchain, balance: str):
        asset_on_blockchain = AssetOnBlockchain.objects.filter(blockchain=blockchain, asset=asset).last()
        if not asset_on_blockchain:
            self._logger.warning(f"Asset {asset} not found on blockchain {blockchain}")
            return

        wallet_with_asset_on_blockchain, created = WalletWithAssetOnBlockchain.objects.get_or_create(
            asset_on_blockchain=asset_on_blockchain,
            wallet=wallet
        )

        # Remove asset for all assets, then after scan set remained asset balances as 0
        try:
            self._all_assets.remove(wallet_with_asset_on_blockchain)
        except ValueError:
            pass

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

    def save_all_assets(self, wallet):
        if self.BLOCKCHAIN_NAME:
            self._all_assets = [asset for asset in WalletWithAssetOnBlockchain.objects.filter(
                wallet=wallet,
                asset_on_blockchain__blockchain__name=self.BLOCKCHAIN_NAME
            ).all()]

    def reset_remain_assets(self):
        for asset in self._all_assets:
            asset: WalletWithAssetOnBlockchain = asset

            if int(asset.history.last().balance) != 0:
                WalletHistoryWithAssetOnBlockchain.objects.create(
                    wallet_with_asset_on_blockchain=asset,
                    balance=0
                )
                self._logger.info("Balance not found in scan. Setting balance as 0: {asset}")

    async def scan_all_wallet(self):
        wallets = Wallet.objects.all()

        for wallet in wallets:
            if self.match_address(wallet.address):
                self.save_all_assets(wallet)
                await self.scan_wallet(wallet)
                self.reset_remain_assets()

    async def run(self):
        return await self.scan_all_wallet()


class NFTProvider(Provider):
    def _get_all_known_ids(self, blockchain: Blockchain, wallet: Wallet):
        return [(nft.token_id, nft.category.category_id) for nft in NFT.objects.filter(blockchain=blockchain, wallet=wallet).all()]

    def _get_or_create_category(self, category_id: str, name: str):
        category, created = NFTCategory.objects.get_or_create(category_id=category_id, name=name)

        if created:
            self._logger.info(f"Found new NFT category: {category}")

        return category

    def _remove_token(self, category_id: str, token_id: str):
        nft = NFT.objects.filter(token_id=token_id, category__category_id=category_id)
        self._logger.info(f"Found removed NFT: {nft}")
        nft.delete()

    def _add_token(
            self,
            blockchain: Blockchain,
            wallet: Wallet,
            category: NFTCategory,
            token_id: str,
            name: str,
            details: dict = None
    ):
        nft = NFT.objects.create(
            blockchain=blockchain,
            wallet=wallet,
            category=category,
            token_id=token_id,
            name=name,
            details=details or {}
        )
        self._logger.info(f"Found new NFT: {nft}")

    async def match_address(self, address: str):
        raise NotImplementedError

    async def scan_wallet(self, wallet: Wallet):
        raise NotImplementedError

    async def scan_all_wallet(self):
        wallets = Wallet.objects.all()

        for wallet in wallets:
            if self.match_address(wallet.address):
                await self.scan_wallet(wallet)

    async def run(self):
        await self.scan_all_wallet()
