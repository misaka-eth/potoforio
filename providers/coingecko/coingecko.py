from providers import PriceProvider


class CoingeckoClient(PriceProvider):
    API_URL = 'https://api.coingecko.com/api/v3'

    async def scan(self):
        ids = {
            'ETH': 'ethereum',
            'WETH': 'weth',
            'USDT': 'tether',
            'BTC': 'bitcoin',
            'LTC': 'litecoin',
            'XRP': 'ripple',
            'CRO': 'crypto-com-chain',
            'MATIC': 'matic-network'
        }

        for ticker, gecko_name in ids.items():
            url = f"{self.API_URL}/simple/price?ids={gecko_name}&vs_currencies=usd"

            response = await self._request('GET', url)
            response = await response.json()

            price = response.get(gecko_name).get('usd', None)

            if not price:
                self._logger.warning(f"Can't update price for ticker {ticker}. Error: {response}")

            await self._update_price(ticker=ticker, price=price)
