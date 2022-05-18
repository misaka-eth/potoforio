from potoforio.providers import NFTProvider

from potoforio.core.models import Wallet, Blockchain


class ThegraphNFTProvider(NFTProvider):
    BLOCKCHAIN_NAME = "Gnosis"
    API_URL = 'https://api.thegraph.com/subgraphs/name/sunguru98/erc721-xdai-subgraph'

    async def scan_wallet(self, wallet: Wallet):
        json = {
            "query": "\n  query Get721Tokens($owner: ID) {\n    tokens(first: 1000, where: { owner: $owner }) {\n     "
                     " tokenUri: uri\n      tokenId: identifier\n      token: registry {\n        address: id\n       "
                     " name\n        symbol\n      }\n    }\n  }\n",
            "variables": {
                "owner": wallet.address
            }
        }

        response = await self._request('POST', self.API_URL, json=json)
        response = await response.json()

        result = response.get('data').get('tokens')

        blockchain = Blockchain.objects.get(name=self.BLOCKCHAIN_NAME)

        for nft in result:
            token_uri = nft.get('tokenUri')
            category_name = nft.get('token').get('name')
            address = nft.get('token').get('address')
            token_id = nft.get('tokenId')

            # Save category name and token_uri as base
            name = category_name
            image = token_uri
            import json

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
