from potoforio.core.models import Blockchain, Asset, AssetOnBlockchain
import logging

LOGGER = logging.getLogger(__name__)

BITCOIN = "Bitcoin"
ETHEREUM = "Ethereum"
ETHEREUM_VALIDATOR = "Ethereum Validator"
LITECOIN = "Litecoin"
RIPPLE = "Ripple"
CRYPTOORG = "Crypto.com"
POLYGON = 'Polygon'
TRON = 'Tron'
BSC = 'BSC'

blockchains = [
    {
        "name": ETHEREUM,
        "explorer": "https://etherscan.io/address/",
        "nft_explorer": 'https://etherscan.io/nft/'
    },
    {"name": ETHEREUM_VALIDATOR, "explorer": "https://beaconscan.com/validator/"},
    {"name": BITCOIN, "explorer": "https://blockchair.com/ru/bitcoin/address/"},
    {"name": LITECOIN, "explorer": "https://blockchair.com/ru/litecoin/address/"},
    {"name": RIPPLE, "explorer": "https://xrpscan.com/account/"},
    {
        "name": CRYPTOORG,
        "explorer": "https://crypto.org/explorer/account/",
        "nft_explorer": "https://crypto.org/explorer/nfts/tokens/"
    },
    {"name": POLYGON, "explorer": "https://polygonscan.com/address/"},
    {"name": TRON, "explorer": "https://tronscan.org/#/address/"},
    {"name": BSC, "explorer": "https://bscscan.com/address/"}
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
    {'name': "USD Coin", "ticker": "USDC", "decimals": 6},
    {'name': 'Tron', 'ticker': 'TRX', 'decimals': 6}
]

assets_on_blockchains = [
    # Native
    (ETHEREUM, "ETH", None),
    (BITCOIN, "BTC", None),
    (LITECOIN, "LTC", None),
    (RIPPLE, "XRP", None),
    (CRYPTOORG, "CRO", None),
    (ETHEREUM_VALIDATOR, "ETH", None),
    (TRON, 'TRX', None),

    # Ethereum blockchain
    (ETHEREUM, "WETH", "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"),
    (ETHEREUM, "USDT", "0xdac17f958d2ee523a2206206994597c13d831ec7"),

    # Polygon blockchain
    (POLYGON, "USDT", "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"),
    (POLYGON, "MATIC", "0x0000000000000000000000000000000000001010"),
    (POLYGON, "WETH", "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619"),
    (POLYGON, "USDC", "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"),

    # Tron blockchain
    (TRON, "USDT", 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
]


def init_data():
    # If any data already exists
    # if Blockchain.objects.first():
    #     LOGGER.info("Initial data already exists")
    #     return

    for blockchain in blockchains:
        if not Blockchain.objects.filter(
            name=blockchain['name']
        ):
            Blockchain.objects.create(
                name=blockchain['name'],
                explorer=blockchain.get('explorer'),
                nft_explorer=blockchain.get('nft_explorer', ''))

    for asset in assets:
        if not Asset.objects.filter(ticker=asset['ticker']):
            Asset.objects.get_or_create(
                name=asset['name'],
                ticker=asset['ticker'],
                decimals=asset['decimals']
            )

    for asset_on_blockchain in assets_on_blockchains:
        blockchain_name, asset_ticker, address = asset_on_blockchain
        blockchain = Blockchain.objects.filter(name=blockchain_name).first()
        asset = Asset.objects.filter(ticker=asset_ticker).first()

        # Keep all address if lowercase
        if address:
            address = address.lower()

        if not AssetOnBlockchain.objects.filter(
            blockchain=blockchain, asset=asset
        ):
            AssetOnBlockchain.objects.create(blockchain=blockchain, asset=asset, address=address)

    LOGGER.info("Initial data created")
