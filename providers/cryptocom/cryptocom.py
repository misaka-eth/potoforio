from providers import BalanceProvider, NFTProvider

from core.models import Asset, Wallet, Blockchain


class CryptocomClient(BalanceProvider):
    API_URL = 'https://crypto.org/explorer/api/v1'

    async def scan_wallet(self, wallet: Wallet):
        url = f"{CryptocomClient.API_URL}/accounts/{wallet.address}"
        response = await self._request('GET', url)
        response = await response.json()

        blockchain_cryptocom = Blockchain.objects.filter(name="Crypto.com").last()
        asset_cro = Asset.objects.filter(ticker='CRO').last()

        balance = str(int(float(response.get('result').get('totalBalance')[0].get('amount'))))
        await self._update_balance(
            wallet=wallet,
            blockchain=blockchain_cryptocom,
            asset=asset_cro,
            balance=balance
        )

    def match_address(self, address: str):
        return address.startswith('cro1')


class CryptocomNFTProvider(NFTProvider):
    API_URL = 'https://crypto.org/explorer/api/v1'

    async def scan_wallet(self, wallet: Wallet):
        url = f'{CryptocomNFTProvider.API_URL}/nfts/accounts/{wallet.address}/tokens'
        params = {
            'pagination': 'offset',
            'page': 1,
            'limit': 10000,
            'order': 'height.desc'
        }
        response = await self._request('GET', url, params=params)
        response = await response.json()

        blockchain = Blockchain.objects.filter(name="Crypto.com").last()

        known_ids = self._get_all_known_ids(blockchain=blockchain, wallet=wallet)

        for token in response.get('result'):
            denom_id = token.get('denomId')
            denom_name = token.get('denomName')

            token_id = token.get('tokenId')
            token_name = token.get('tokenName')

            # Crypto.com drops generate denom name same as denom id, for more information we use token name instead
            if denom_id == denom_name:
                denom_name = token_name

            category = self._get_or_create_category(category_id=denom_id, name=denom_name)

            try:
                known_ids.remove((token_id, denom_id))
            except ValueError:
                # If token doesn't exists
                self._add_token(
                    blockchain=blockchain,
                    wallet=wallet,
                    category=category,
                    token_id=token_id,
                    name=token_name,
                    details=token
                )

        # Remove token, that exist before, but now missing
        for token_id, denom_id in known_ids:
            self._remove_token(category_id=denom_id, token_id=token_id)

    def match_address(self, address: str):
        return address.startswith('cro1')
