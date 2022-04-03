from potoforio.providers import PriceProvider, ProviderConnectionError


class CoingeckoClient(PriceProvider):
    API_URL = 'https://api.coingecko.com/api/v3'

    async def scan(self):
        coingecho_ids = {
            'ETH': 'ethereum',
            'WETH': 'weth',
            'USDT': 'tether',
            'BTC': 'bitcoin',
            'LTC': 'litecoin',
            'XRP': 'ripple',
            'CRO': 'crypto-com-chain',
            'MATIC': 'matic-network'
        }

        coingecho_ids_revers = {value: key for key, value in coingecho_ids.items()}
        coingecho_ids_str = ",".join(coingecho_ids.values())

        url = f"{self.API_URL}/simple/price?ids={coingecho_ids_str}&vs_currencies=usd"

        try:
            response = await self._request('GET', url)
        except ProviderConnectionError:
            self._logger.warning(f"ProviderConnectionError")
            return

        response = await response.json()

        for asset in response.keys():
            ticker = coingecho_ids_revers.pop(asset)
            price = response[asset]['usd']

            await self._update_price(ticker=ticker, price=price)

        if coingecho_ids_revers:
            self._logger.warning(f"Can't update prices for: {','.join(coingecho_ids_revers.keys())}")
