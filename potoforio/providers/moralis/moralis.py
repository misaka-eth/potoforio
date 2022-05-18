
from potoforio.providers import NFTProvider

from potoforio.core.models import Wallet, Blockchain


class MoralisNFTProvider(NFTProvider):
    BLOCKCHAIN_NAME = "BSC"
    API_URL = 'https://deep-index.moralis.io/api/v2/{wallet}/nft?chain={chain}&format=decimal'

    @staticmethod
    def get_default_configuration():
        configuration = NFTProvider.get_default_configuration()
        configuration['api_key'] = ''
        return configuration

    async def scan_wallet(self, wallet: Wallet):
        api_key = self.get_configuration('api_key')
        if not api_key:
            self._logger.warning("Need api key")
            return

        url = self.API_URL.format(
            wallet=wallet.address,
            chain='bsc'
        )
        headers = {
            'X-API-Key': api_key
        }
        response = await self._request('GET', url, headers=headers)
        response = await response.json()

        result = response.get('result', [])

        blockchain = Blockchain.objects.get(name=self.BLOCKCHAIN_NAME)

        for nft in result:
            token_uri = nft.get('token_uri')
            category_name = nft.get('name')
            address = nft.get('token_address')
            token_id = nft.get('token_id')
            metadata = nft.get('metadata')

            # Save category name and token_uri as base
            name = category_name
            image = token_uri
            import json

            # Fetch data from metadata
            if metadata:
                metadata = json.loads(metadata)
                image = metadata.get('image_url')
                name = metadata.get('name')

            # Fetch data from token_uri
            if token_uri:
                response = await self._request('GET', token_uri)

                if response.status == 200:
                    response = await response.text()
                    response = json.loads(response)
                    image = response.get('image') or response.get('image_url')
                    name = response.get('name')

            category = self._get_or_create_category(category_id=address, name=category_name)

            self._add_token(
                blockchain=blockchain,
                wallet=wallet,
                category=category,
                token_id=str(token_id),
                name=name,
                details=nft,
                image_url=image
            )

    def match_address(self, address: str):
        return len(address) == 42 and address.startswith('0x')
