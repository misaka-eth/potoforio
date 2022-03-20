import logging
import aiohttp

from core.models import Token, TokenPriceHistory, TokenOnBlockchain, WalletWithTokenOnBlockchain, Blockchain, Wallet, \
    WalletHistoryWithTokenOnBlockchain


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

        tokens = Token.objects.filter(ticker=ticker).all()
        if not tokens:
            self._logger.warning(f"Can't find token {ticker}.")
            return
        for token in tokens:
            log_prefix = f"Update price for token: {token} -"
            last_price = TokenPriceHistory.objects.filter(token=token).order_by('timestamp').last()
            if not last_price or last_price.price != price:
                if last_price:
                    price_difference = price - last_price.price
                    price_difference_str = f"{'+' if price_difference > 0 else ''}{price_difference:.2f}"
                else:
                    price_difference_str = "~"
                self._logger.info(f"{log_prefix} New price: {price} ({price_difference_str})")
                TokenPriceHistory.objects.create(token=token, price=price)
            else:
                self._logger.debug(f"{log_prefix} Skip update: price doesn't change")


class BalanceProvider(Provider):
    async def _update_balance(self, wallet: Wallet, token: Token, blockchain: Blockchain, balance: str):
        token_on_blockchain = TokenOnBlockchain.objects.filter(blockchain=blockchain, token=token).last()
        if not token_on_blockchain:
            self._logger.warning(f"Token {token} not found on blockchain {blockchain}")
            return

        wallet_with_token_on_blockchain, created = WalletWithTokenOnBlockchain.objects.get_or_create(
            token_on_blockchain=token_on_blockchain,
            wallet=wallet
        )

        if created:
            self._logger.info(f"Found {wallet_with_token_on_blockchain}")

        last_record = WalletHistoryWithTokenOnBlockchain.objects.filter(
            wallet_with_token_on_blockchain=wallet_with_token_on_blockchain
        ).last()

        if last_record and last_record.balance == balance:
            self._logger.debug(f"Balance not changed")
            return

        WalletHistoryWithTokenOnBlockchain.objects.create(
            wallet_with_token_on_blockchain=wallet_with_token_on_blockchain,
            balance=str(balance)
        )
        last_record_balance = "0" if not last_record else last_record.balance
        self._logger.info(f"Balance for {wallet_with_token_on_blockchain} updated. {last_record_balance}->{balance}")

        return
