from rest_framework import serializers

from .models import Blockchain, Token, Wallet, TokenOnBlockchain, WalletWithTokenOnBlockchain, \
    WalletHistoryWithTokenOnBlockchain, TokenPriceHistory, BalanceHistory


class BlockchainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blockchain
        fields = '__all__'


class WalletHistoryWithTokenOnBlockchainSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletHistoryWithTokenOnBlockchain
        fields = '__all__'


class TokenOnBlockchainSerializerForTokenSerializer(serializers.ModelSerializer):
    blockchain = BlockchainSerializer()
    history = WalletHistoryWithTokenOnBlockchainSerializer(many=True, read_only=True)

    class Meta:
        model = TokenOnBlockchain
        fields = ['id', 'address', 'blockchain', 'history']


class TokenSerializer(serializers.ModelSerializer):
    last_price = serializers.SerializerMethodField(read_only=True)
    tokens_on_blockchains = TokenOnBlockchainSerializerForTokenSerializer(many=True, read_only=True)

    class Meta:
        model = Token
        fields = ['id', 'name', 'ticker', 'decimals', 'last_price', 'tokens_on_blockchains']

    def get_last_price(self, token: Token):
        price_data = TokenPriceHistory.objects.filter(token=token).order_by('timestamp').last()
        return price_data.price if price_data else 0


class TokenOnBlockchainSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenOnBlockchain
        fields = '__all__'


class TokenOnBlockchainSerializerForWalletWithTokenOnBlockchainSerializerForWalletSerializer(serializers.ModelSerializer):
    blockchain = BlockchainSerializer()
    token = TokenSerializer()

    class Meta:
        model = TokenOnBlockchain
        fields = ['id', 'address', 'blockchain', 'token']


class WalletWithTokenOnBlockchainSerializerForWalletSerializer(serializers.ModelSerializer):
    token_on_blockchain = TokenOnBlockchainSerializerForWalletWithTokenOnBlockchainSerializerForWalletSerializer()
    # history = WalletHistoryWithTokenOnBlockchainSerializer(many=True, read_only=True)
    balance = serializers.SerializerMethodField()

    class Meta:
        model = WalletWithTokenOnBlockchain
        fields = ['id', 'token_on_blockchain', 'balance']

    def get_balance(self, instance: WalletWithTokenOnBlockchain):
        return WalletHistoryWithTokenOnBlockchainSerializer(instance.history.last(), many=False).data


class WalletSerializer(serializers.ModelSerializer):
    tokens_on_blockchains = WalletWithTokenOnBlockchainSerializerForWalletSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'name', 'address', 'tokens_on_blockchains']


class BalanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceHistory
        fields = ['timestamp', 'balance']
