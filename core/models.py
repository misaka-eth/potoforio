from django.db import models


class Blockchain(models.Model):
    """
    Blockchain is infrastructure for tokens/coins.
    """
    name = models.CharField(max_length=200, unique=True)
    explorer = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Token(models.Model):
    """
    Token/Coin is valuable that stored on blockchain
    """
    name = models.CharField(max_length=200)
    ticker = models.CharField(max_length=10, unique=True)
    decimals = models.IntegerField()

    blockchains = models.ManyToManyField(Blockchain, through='TokenOnBlockchain')

    def __str__(self):
        return f"{self.ticker} | {self.name}"


class Wallet(models.Model):
    """
    Wallet is hashed public key, that use to define user account on blockchains.
    Wallet can be used on different blockchain (ETH/BTC/Cronos).
    """
    name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} {self.address}"


class TokenOnBlockchain(models.Model):
    """
    Any token can be represented on different blockchain via bridges, in this case we can track token by address.
    Native tokens usual doesn't have address.
    """
    blockchain = models.ForeignKey(Blockchain, on_delete=models.CASCADE)
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='tokens_on_blockchains')
    address = models.CharField(max_length=200, null=True)

    class Meta:
        unique_together = ('blockchain', 'token',)

    def __str__(self):
        return f"{self.token} on {self.blockchain}"


class WalletWithTokenOnBlockchain(models.Model):
    """
    If wallet has token on specific blockchain record it here.
    """
    token_on_blockchain = models.ForeignKey(TokenOnBlockchain, on_delete=models.CASCADE, related_name='wallets')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='tokens_on_blockchains')

    class Meta:
        unique_together = ('token_on_blockchain', 'wallet',)

    def __str__(self):
        return f"Wallet {self.wallet} with {self.token_on_blockchain}"


class WalletHistoryWithTokenOnBlockchain(models.Model):
    """
    Wallet have balance history.
    History collected at specific time or can be specified by user.
    """
    wallet_with_token_on_blockchain = models.ForeignKey(WalletWithTokenOnBlockchain, on_delete=models.CASCADE, related_name='history')

    timestamp = models.DateTimeField(auto_now_add=True)
    balance = models.CharField(max_length=200)
    manual = models.BooleanField(default=False)

    class Meta:
        unique_together = ('wallet_with_token_on_blockchain', 'timestamp', 'balance')


class TokenPriceHistory(models.Model):
    """
    Token price for balance calculating
    """
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="prices")
    timestamp = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()

    class Meta:
        unique_together = ('token', 'timestamp', 'price')


class BalanceHistory(models.Model):
    """
    History of total balance in USD
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    balance = models.FloatField()
