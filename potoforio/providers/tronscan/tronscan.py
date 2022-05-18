from potoforio.providers import BalanceProvider

from potoforio.core.models import Asset, Wallet, Blockchain, AssetOnBlockchain


class TronscanBalanceProvider(BalanceProvider):
    API_URL = 'https://apilist.tronscan.org/api'
    BLOCKCHAIN_NAME = "Tron"

    async def scan_wallet(self, wallet: Wallet):
        # TODO: Pagination ?
        url = f"{self.API_URL}/account/tokens"
        params = {"address": wallet.address}

        response = await self._request('GET', url, params=params)
        response = await response.json()

        blockchain = Blockchain.objects.filter(name=self.BLOCKCHAIN_NAME).last()

        for token in response.get('data'):
            balance = token.get('balance')
            ticker = token.get('tokenAbbr').upper()
            token_id = token.get('tokenId').lower()

            if token_id == '_':
                asset = Asset.objects.filter(ticker='TRX').last()
            else:
                asset_on_trx = AssetOnBlockchain.objects.filter(address=token_id).last()
                if not asset_on_trx:
                    self._logger.warning(f'Unknown asset: {balance} {ticker} with address {token_id}')
                    continue
                asset = asset_on_trx.asset

            await self._update_balance(
                wallet=wallet,
                blockchain=blockchain,
                asset=asset,
                balance=str(balance)
            )

    def match_address(self, address: str):
        return address.startswith('T')
