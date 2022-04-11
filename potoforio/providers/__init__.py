import logging
import aiohttp

from potoforio.core.models import Asset, AssetPriceHistory, AssetOnBlockchain, WalletWithAssetOnBlockchain, \
    Blockchain, Wallet, WalletHistoryWithAssetOnBlockchain, NFT, NFTCategory

from potoforio.potoforio.settings import DEBUG_HTTP


class ProviderException(Exception):
    pass


class ProviderConnectionError(Exception):
    pass


class ProviderInvalidResponse(ProviderException):
    pass


class Provider:
    def __init__(self, configuration: dict):
        self._configuration = configuration
        self._logger = logging.getLogger(self.__class__.__name__)

    async def _request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """
        aiohttp requests with custom logger and error handling
        """
        if DEBUG_HTTP:
            self._logger.debug(f">> Request {method} {url} {kwargs}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, url, **kwargs) as response:
                    read = await response.read()
                    if DEBUG_HTTP:
                        self._logger.debug(f"<< Response {read}")
                    return response
            except aiohttp.ClientConnectorError as error:
                raise ProviderConnectionError from error

    @staticmethod
    def get_default_configuration() -> dict:
        """
        Called on first register event.
        Must return dict of default parameters
        """
        return {
            "timeout": 60
        }

    def get_configuration(self, key: str):  # -> int | float | dict | list:
        return self._configuration.get(key)

    async def run(self) -> None:
        """
        Identical entry point for all providers
        """
        raise NotImplementedError


class PriceProvider(Provider):
    async def _update_price(self, ticker: str, price: float) -> None:
        assets = Asset.objects.filter(ticker=ticker).all()
        if not assets:
            self._logger.warning(f"Can't find asset {ticker}.")
            return
        for asset in assets:
            log_prefix = f"Update price for asset: {asset} -"
            last_price = AssetPriceHistory.objects.filter(asset=asset).order_by('timestamp').last()
            is_price_changed = last_price and last_price.price != price
            if is_price_changed:
                if last_price:
                    price_difference = price - last_price.price
                    price_difference_str = f"{'+' if price_difference > 0 else ''}{price_difference:.2f}"
                else:
                    price_difference_str = "~"
                self._logger.debug(f"{log_prefix} New price: {price} ({price_difference_str})")
                AssetPriceHistory.objects.create(asset=asset, price=price)
            else:
                self._logger.debug(f"{log_prefix} Skip update: price doesn't change")

    async def scan(self) -> None:
        raise NotImplementedError

    async def run(self) -> None:
        return await self.scan()


class BalanceProvider(Provider):
    BLOCKCHAIN_NAME = ""

    def __init__(self, configuration: dict):
        super().__init__(configuration)
        self._all_assets = []

    async def _update_balance(self, wallet: Wallet, asset: Asset, blockchain: Blockchain, balance: str) -> None:
        """
        Update balance for given address
        """
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
            # New asset doesn't exist in this list
            pass

        if created:
            self._logger.info(f"Found {wallet_with_asset_on_blockchain}")

        last_record = WalletHistoryWithAssetOnBlockchain.objects.filter(
            wallet_with_asset_on_blockchain=wallet_with_asset_on_blockchain
        ).last()

        is_balance_changed = last_record and last_record.balance != balance
        if not is_balance_changed:
            self._logger.debug(f"Balance not changed for {wallet_with_asset_on_blockchain}")
            return

        WalletHistoryWithAssetOnBlockchain.objects.create(
            wallet_with_asset_on_blockchain=wallet_with_asset_on_blockchain,
            balance=balance
        )
        last_record_balance = "0" if not last_record else last_record.balance
        self._logger.info(f"Balance for {wallet_with_asset_on_blockchain} updated. {last_record_balance}->{balance}")

        return

    def match_address(self, address: str) -> bool:
        """
        Return true if address match blockchain, thus can be scanned for assets
        """
        raise NotImplementedError

    async def scan_wallet(self, wallet: Wallet) -> None:
        """
        Scan wallet for assets
        """
        raise NotImplementedError

    def save_all_assets(self, wallet) -> None:
        """
        Save all assets on wallet
        """
        if self.BLOCKCHAIN_NAME:
            self._all_assets = [asset for asset in WalletWithAssetOnBlockchain.objects.filter(
                wallet=wallet,
                asset_on_blockchain__blockchain__name=self.BLOCKCHAIN_NAME
            ).all()]

    def reset_remain_assets(self) -> None:
        """
        Reset balance for assets than doesn't appear in scan, but persists in db.
        """
        for asset in self._all_assets:
            asset: WalletWithAssetOnBlockchain = asset

            if int(asset.history.last().balance) != 0:
                WalletHistoryWithAssetOnBlockchain.objects.create(
                    wallet_with_asset_on_blockchain=asset,
                    balance=0
                )
                self._logger.info("Balance not found in scan. Setting balance as 0: {asset}")

    async def scan_all_wallet(self) -> None:
        """
        Scan all wallet for assets
        """
        wallets = Wallet.objects.all()

        for wallet in wallets:
            if self.match_address(wallet.address):
                # Save all assets before scan.
                self.save_all_assets(wallet)
                # Scan
                await self.scan_wallet(wallet)
                # Delete unseen assets. They probably removed from wallet
                self.reset_remain_assets()

    async def run(self) -> None:
        return await self.scan_all_wallet()


class NFTProvider(Provider):
    @staticmethod
    def _get_all_known_ids(blockchain: Blockchain, wallet: Wallet) -> list:
        """
        Return list of ids all known NFT on this wallet
        """
        return [(nft.token_id, nft.category.category_id) for nft in NFT.objects.filter(
            blockchain=blockchain,
            wallet=wallet
        ).all()]

    def _get_or_create_category(self, category_id: str, name: str) -> NFTCategory:
        category, created = NFTCategory.objects.get_or_create(category_id=category_id, name=name)

        if created:
            self._logger.info(f"Found new NFT category: {category}")

        return category

    def _remove_token(self, category_id: str, token_id: str) -> None:
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
            details: dict = None,
            image_url: str = None
    ) -> None:
        nft = NFT.objects.create(
            blockchain=blockchain,
            wallet=wallet,
            category=category,
            token_id=token_id,
            name=name,
            details=details or {},
            image_url=image_url
        )
        self._logger.info(f"Found new NFT: {nft}")

    async def match_address(self, address: str) -> bool:
        raise NotImplementedError

    async def scan_wallet(self, wallet: Wallet) -> None:
        raise NotImplementedError

    async def scan_all_wallet(self) -> None:
        wallets = Wallet.objects.all()

        for wallet in wallets:
            if self.match_address(wallet.address):
                await self.scan_wallet(wallet)

    async def run(self) -> None:
        return await self.scan_all_wallet()
