from potoforio.core.models import Blockchain, Asset, AssetOnBlockchain
import logging

LOGGER = logging.getLogger(__name__)

blockchains = [
    {
        "name": "Ethereum",
        "explorer": "https://etherscan.io/address/",
        "nft_explorer": 'https://etherscan.io/nft/'
    },
    {"name": "Ethereum Validator", "explorer": "https://beaconscan.com/validator/"},
    {"name": "Bitcoin", "explorer": "https://blockchair.com/ru/bitcoin/address/"},
    {"name": "Litecoin", "explorer": "https://blockchair.com/ru/litecoin/address/"},
    {"name": "Ripple", "explorer": "https://xrpscan.com/account/"},
    {
        "name": "Crypto.com",
        "explorer": "https://crypto.org/explorer/account/",
        "nft_explorer": "https://crypto.org/explorer/nfts/tokens/"
    },
    {"name": "Polygon", "explorer": "https://polygonscan.com/address/"},
]

assets = [
    {'name': "Ether", "ticker": "ETH", "decimals": 18},
    {'name': "Wrapped Ether", "ticker": "WETH", "decimals": 18},
    {'name': "Thether USD", "ticker": "USDT", "decimals": 6},
    {'name': "Bitcoin", "ticker": "BTC", "decimals": 8},
    {'name': "Litecoin", "ticker": "LTC", "decimals": 8},
    {'name': "Ripple", "ticker": "XRP", "decimals": 6},
    {'name': "Cronos", "ticker": "CRO", "decimals": 8},
    {'name': "Polygon", "ticker": "MATIC", "decimals": 18},
]

assets_on_blockchains = [
    ("Ethereum", "ETH", None),
    ("Ethereum", "WETH", "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"),
    ("Ethereum Validator", "ETH", None),
    ("Ethereum", "USDT", "0xdac17f958d2ee523a2206206994597c13d831ec7"),
    ("Polygon", "USDT", "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"),
    ("Bitcoin", "BTC", None),
    ("Litecoin", "LTC", None),
    ("Ripple", "XRP", None),
    ("Crypto.com", "CRO", None),
    ("Polygon", "MATIC", "0x0000000000000000000000000000000000001010"),
    ("Polygon", "WETH", "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619"),
]


def init_data():
    # If any data already exists
    if Blockchain.objects.first():
        LOGGER.info("Initial data already exists")
        return

    for blockchain in blockchains:
        Blockchain.objects.create(
            name=blockchain['name'],
            explorer=blockchain.get('explorer'),
            nft_explorer=blockchain.get('nft_explorer'))

    for asset in assets:
        Asset.objects.create(
            name=asset['name'],
            ticker=asset['ticker'],
            decimals=asset['decimals']
        )

    for asset_on_blockchain in assets_on_blockchains:
        blockchain_name, asset_ticker, address = asset_on_blockchain
        blockchain = Blockchain.objects.filter(name=blockchain_name).first()
        asset = Asset.objects.filter(ticker=asset_ticker).first()

        AssetOnBlockchain.objects.create(blockchain=blockchain, asset=asset, address=address)

    LOGGER.info("Initial data created")
