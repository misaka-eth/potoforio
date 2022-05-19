from potoforio.providers import BalanceProvider, NFTProvider, ProviderException

from potoforio.core.models import Asset, Wallet, Blockchain


class CryptocomClient(BalanceProvider):
    API_URL = 'https://crypto.org/explorer/api/v1'
    BLOCKCHAIN_NAME = "Crypto.com"

    async def scan_wallet(self, wallet: Wallet):
        url = f"{CryptocomClient.API_URL}/accounts/{wallet.address}"
        response = await self._request('GET', url)
        response = await response.json()

        blockchain_cryptocom = Blockchain.objects.filter(name=self.BLOCKCHAIN_NAME).last()
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
    BLOCKCHAIN_NAME = "Crypto.com"

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

        # Sometimes API return empty (not full?) result list, and pagination return correct length of this list,
        # so we check those lengths to prevent removing existing NFT from DB
        result_len = len(response.get('result'))
        total_record = response.get('pagination').get('total_record')
        if result_len != total_record:
            raise ProviderException(
                f"Got {result_len} elements in result list, but pagination shows {total_record} items"
            )

        for token in response.get('result'):
            denom_id = token.get('denomId')
            denom_name = token.get('denomName')
            image_url = token.get('tokenURI')

            token_id = token.get('tokenId')
            token_name = token.get('tokenName')

            # Crypto.com drops generate denom name same as denom id, for more information we use token name instead
            if denom_id == denom_name:
                denom_name = token_name

            category = self._get_or_create_category(category_id=denom_id, name=denom_name)

            self._add_token(
                blockchain=blockchain,
                wallet=wallet,
                category=category,
                token_id=token_id,
                name=token_name,
                details=token,
                image_url=image_url
            )

    def match_address(self, address: str):
        return address.startswith('cro1')
