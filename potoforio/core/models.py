from django.db import models


class Blockchain(models.Model):
    """
    Blockchain is infrastructure for assets/coins.
    """
    name = models.CharField(max_length=200, unique=True)
    explorer = models.CharField(max_length=200)
    nft_explorer = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Asset(models.Model):
    """
    Asset is valuable that stored on blockchain
    """
    name = models.CharField(max_length=200)
    ticker = models.CharField(max_length=10, unique=True)
    decimals = models.IntegerField()

    blockchains = models.ManyToManyField(Blockchain, through='AssetOnBlockchain')

    def __str__(self):
        return f"{self.ticker} | {self.name}"


class Wallet(models.Model):
    """
    Wallet is hashed public key, that use to define user account on blockchains.
    Wallet can be used on different blockchain (ETH/BTC/Cronos).
    """
    name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f"{self.name} {self.address}"


class AssetOnBlockchain(models.Model):
    """
    Any asset can be represented on different blockchain via bridges, in this case we can track asset by address.
    Native assets usual doesn't have address.
    """
    blockchain = models.ForeignKey(Blockchain, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='assets_on_blockchains')
    address = models.CharField(max_length=200, null=True)

    class Meta:
        unique_together = ('blockchain', 'asset',)

    def __str__(self):
        return f"{self.asset} on {self.blockchain}"


class WalletWithAssetOnBlockchain(models.Model):
    """
    If wallet has asset on specific blockchain record it here.
    """
    asset_on_blockchain = models.ForeignKey(AssetOnBlockchain, on_delete=models.CASCADE, related_name='wallets')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='assets_on_blockchains')

    class Meta:
        unique_together = ('asset_on_blockchain', 'wallet',)

    def __str__(self):
        return f"Wallet {self.wallet} with {self.asset_on_blockchain}"


class WalletHistoryWithAssetOnBlockchain(models.Model):
    """
    Wallet have balance history.
    History collected at specific time or can be specified by user.
    """
    wallet_with_asset_on_blockchain = models.ForeignKey(WalletWithAssetOnBlockchain, on_delete=models.CASCADE,
                                                        related_name='history')

    timestamp = models.DateTimeField(auto_now_add=True)
    balance = models.CharField(max_length=200)
    manual = models.BooleanField(default=False)

    class Meta:
        unique_together = ('wallet_with_asset_on_blockchain', 'timestamp', 'balance')


class AssetPriceHistory(models.Model):
    """
    Asset price for balance calculating
    """
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="prices")
    timestamp = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()

    class Meta:
        unique_together = ('asset', 'timestamp', 'price')


class BalanceHistory(models.Model):
    """
    History of total balance in USD
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    balance = models.FloatField()


class Provider(models.Model):
    """
    Registered providers
    """
    REGISTERED = 1
    ACTIVE = 2
    PAUSED = 3
    NOT_FOUND = 4
    STATUS = (
        (REGISTERED, 'Registered'),
        (ACTIVE, 'Active'),
        (PAUSED, 'Paused'),
        (NOT_FOUND, 'Not found')
    )

    name = models.CharField(max_length=200, unique=True)
    path = models.CharField(max_length=200)
    status = models.PositiveSmallIntegerField(choices=STATUS, default=REGISTERED)

    configuration = models.JSONField()

    @classmethod
    def register(cls, name: str, path: str, configuration: dict):
        provider = cls.objects.filter(name=name).first()

        # If record not exists, create one
        if not provider:
            return cls.objects.create(name=name, path=path, configuration=configuration)

        # Update
        provider.status = Provider.REGISTERED
        provider.path = path
        provider.save()

        return provider

    @classmethod
    def unregister_all(cls):
        cls.objects.update(status=Provider.NOT_FOUND)

    def __str__(self):
        return f'<Provider name="{self.name}" path="{self.path}">'


class ProviderHistory(models.Model):
    """
    Providers running history
    """
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="history")
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField(auto_now_add=True)
    error = models.CharField(max_length=200, null=True)


class NFTCategory(models.Model):
    """
    NFT class in different blockchain is different type.
    EVM using "Contract address".
    Crypto.com using "Denom".
    But in any case it's represent category of NFT.
    """
    category_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f'<NFTCategory name="{self.name}" category_id="{self.category_id}">'


class NFT(models.Model):
    """
    Non Fungible Token
    """
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="NFTs")
    blockchain = models.ForeignKey(Blockchain, on_delete=models.CASCADE, related_name="NFTs")
    token_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(NFTCategory, on_delete=models.CASCADE, related_name="NFTs")
    details = models.JSONField()

    class Meta:
        unique_together = ('token_id', 'category',)

    def __str__(self):
        return f'<NFT token_id="{self.token_id}" category="{self.category}">'
