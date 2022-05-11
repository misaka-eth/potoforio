import datetime
import logging
import aiohttp
import pytz

from potoforio.core.models import Asset, AssetOnBlockchain, WalletWithAssetOnBlockchain, \
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
                raise error

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
    async def _update_price(self, ticker: str, price: float, h24_change: float = None, timestamp: int = None) -> None:
        assets = Asset.objects.filter(ticker=ticker).all()
        if not assets:
            self._logger.warning(f"Can't find asset {ticker}.")
            return
        for asset in assets:
            log_prefix = f"Update price for asset: {asset} -"
            is_price_changed = not asset.last_price or asset.last_price != price
            if is_price_changed:
                if asset.last_price:
                    price_difference = price - asset.last_price
                    price_difference_str = f"{'+' if price_difference > 0 else ''}{price_difference:.2f}"
                else:
                    price_difference_str = "~"
                self._logger.debug(f"{log_prefix} New price: {price} ({price_difference_str})")
                asset.last_price = price
                asset.price_timestamp = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
                asset.price_24h_change = h24_change
                asset.save()
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
    BLOCKCHAIN_NAME = None

    def __init__(self, configuration: dict):
        super().__init__(configuration)
        self._all_nfts = []

    def _get_or_create_category(self, category_id: str, name: str) -> NFTCategory:
        category, created = NFTCategory.objects.get_or_create(category_id=category_id, name=name)

        if created:
            self._logger.info(f"Found new NFT category: {category}")

        return category

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
        nft = NFT.objects.filter(token_id=token_id, category=category).last()

        if not nft:
            nft, created = NFT.objects.get_or_create(
                blockchain=blockchain,
                wallet=wallet,
                category=category,
                token_id=token_id,
                name=name,
                details=details or {},
                image_url=image_url
            )
            self._logger.info(f"Found new NFT: {nft}")
        else:
            # if nft exists and found again remove it from list
            try:
                self._all_nfts.remove(nft)
            except ValueError:
                print(nft)

    async def match_address(self, address: str) -> bool:
        raise NotImplementedError

    async def scan_wallet(self, wallet: Wallet) -> None:
        raise NotImplementedError

    async def save_all_nft(self, wallet: Wallet) -> None:
        self._all_nfts = [nft for nft in NFT.objects.filter(
            blockchain__name=self.BLOCKCHAIN_NAME,
            wallet=wallet
        ).all()]

    async def reset_remain_nfts(self) -> None:
        """
        Remove NFTs and not found in current scan
        """
        for nft in self._all_nfts:
            nft: NFT = nft
            self._logger.info(f"Removing NFT: {nft}")
            nft.delete()

    async def scan_all_wallet(self) -> None:
        wallets = Wallet.objects.all()

        for wallet in wallets:
            if self.match_address(wallet.address):
                await self.save_all_nft(wallet)
                await self.scan_wallet(wallet)
                await self.reset_remain_nfts()

    async def run(self) -> None:
        return await self.scan_all_wallet()
