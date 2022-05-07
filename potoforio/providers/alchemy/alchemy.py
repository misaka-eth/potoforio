
from potoforio.providers import NFTProvider

from potoforio.core.models import Wallet, Blockchain


class AlchemyNFTProvider(NFTProvider):
    BLOCKCHAIN_NAME = None
    API_URL = None

    async def scan_wallet(self, wallet: Wallet):
        if not self.BLOCKCHAIN_NAME or not self.API_URL:
            raise Exception("Can't initialize without BLOCKCHAIN and API_URL")
        url = f'{self.API_URL}/getNFTs'
        params = {
            'owner': wallet.address,
        }
        response = await self._request('GET', url, params=params)
        response = await response.json()

        blockchain = Blockchain.objects.get(name=self.BLOCKCHAIN_NAME)

        for nft in response.get('ownedNfts'):
            token_address = nft.get('contract').get('address')

            token_id = nft.get('id').get('tokenId')
            token_id = int(token_id, 16)
            token_media = nft.get('metadata').get('image_url') or nft.get('metadata').get('image')
            token_name = nft.get('metadata').get('name')

            error = nft.get('error')
            if error:
                self._logger.warning(error)

            if not token_name:
                token_name = f'Unknown'

            category = self._get_or_create_category(category_id=token_address, name=token_address)

            self._add_token(
                blockchain=blockchain,
                wallet=wallet,
                category=category,
                token_id=str(token_id),
                name=token_name,
                details=nft,
                image_url=token_media
            )

    def match_address(self, address: str):
        return len(address) == 42 and address.startswith('0x')


class AlchemyEthereumNFTProvider(AlchemyNFTProvider):
    BLOCKCHAIN_NAME = 'Ethereum'
    API_URL = 'https://eth-mainnet.alchemyapi.io/v2/demo'


class AlchemyPolygonNFTProvider(AlchemyNFTProvider):
    BLOCKCHAIN_NAME = 'Polygon'
    API_URL = 'https://polygon-mainnet.g.alchemyapi.io/v2/demo'
