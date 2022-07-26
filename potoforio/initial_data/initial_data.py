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
GNOSIS = "Gnosis"
OPTIMISM = "Optimism"

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
    {"name": BSC, "explorer": "https://bscscan.com/address/"},
    {"name": GNOSIS, "explorer": "https://blockscout.com/xdai/mainnet/address/"},
    {"name": OPTIMISM, "explorer": "https://optimistic.etherscan.io/address/"}
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
    {'name': "Wrapped Polygon", "ticker": "WMATIC", "decimals": 18},
    {'name': "USD Coin", "ticker": "USDC", "decimals": 6},
    {'name': 'Tron', 'ticker': 'TRX', 'decimals': 6},
    {'name': 'xDai', 'ticker': 'DAI', 'decimals': 18},
    {'name': 'Lido Staked ETH', 'ticker': 'stETH', 'decimals': 18},
    {'name': 'Rocket Pool ETH', 'ticker': 'rETH', 'decimals': 18},
]

assets_on_blockchains = [
    # Native ETH
    (ETHEREUM, "ETH", None),
    (OPTIMISM, "ETH", None),
    # Native
    (BITCOIN, "BTC", None),
    (LITECOIN, "LTC", None),
    (RIPPLE, "XRP", None),
    (CRYPTOORG, "CRO", None),
    (ETHEREUM_VALIDATOR, "ETH", None),
    (TRON, 'TRX', None),
    (GNOSIS, 'DAI', None),

    # Ethereum blockchain
    (ETHEREUM, "WETH", "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"),
    (ETHEREUM, "USDT", "0xdac17f958d2ee523a2206206994597c13d831ec7"),
    (ETHEREUM, "stETH", "0xae7ab96520de3a18e5e111b5eaab095312d7fe84"),
    (ETHEREUM, "rETH", "0xae78736cd615f374d3085123a210448e74fc6393"),

    # Polygon blockchain
    (POLYGON, "USDT", "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"),
    (POLYGON, "MATIC", "0x0000000000000000000000000000000000001010"),
    (POLYGON, "WMATIC", "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270"),
    (POLYGON, "WETH", "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619"),
    (POLYGON, "USDC", "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"),

    # Tron blockchain
    (TRON, "USDT", 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'),

    # Optimism
    (OPTIMISM, "USDC", "0x7f5c764cbc14f9669b88837ca1490cca17c31607"),
    (OPTIMISM, "USDT", "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58"),
    (OPTIMISM, "rETH", "0x9bcef72be871e61ed4fbbc7630889bee758eb81d"),
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
        asset_db = Asset.objects.filter(ticker=asset['ticker']).first()
        if not asset_db:
            asset_db = Asset.objects.create(
                name=asset['name'],
                ticker=asset['ticker'],
                decimals=asset['decimals']
            )

        # Rename asset if needed
        if asset_db.name != asset['name']:
            asset_db.name = asset['name']
            asset_db.save()

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
