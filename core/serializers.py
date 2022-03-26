from rest_framework import serializers

from .models import Blockchain, Asset, Wallet, AssetOnBlockchain, WalletWithAssetOnBlockchain, \
    WalletHistoryWithAssetOnBlockchain, AssetPriceHistory, BalanceHistory, Provider, ProviderHistory


class BlockchainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blockchain
        fields = '__all__'


class WalletHistoryWithAssetOnBlockchainSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletHistoryWithAssetOnBlockchain
        fields = '__all__'


class AssetOnBlockchainSerializerForAssetSerializer(serializers.ModelSerializer):
    blockchain = BlockchainSerializer()
    history = WalletHistoryWithAssetOnBlockchainSerializer(many=True, read_only=True)

    class Meta:
        model = AssetOnBlockchain
        fields = ['id', 'address', 'blockchain', 'history']


class AssetSerializer(serializers.ModelSerializer):
    last_price = serializers.SerializerMethodField(read_only=True)
    assets_on_blockchains = AssetOnBlockchainSerializerForAssetSerializer(many=True, read_only=True)

    class Meta:
        model = Asset
        fields = ['id', 'name', 'ticker', 'decimals', 'last_price', 'assets_on_blockchains']

    def get_last_price(self, asset: Asset):
        price_data = AssetPriceHistory.objects.filter(asset=asset).order_by('timestamp').last()
        return price_data.price if price_data else 0


class AssetOnBlockchainSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetOnBlockchain
        fields = '__all__'


class AssetOnBlockchainSerializerForWalletWithAssetOnBlockchainSerializerForWalletSerializer(
    serializers.ModelSerializer
):
    blockchain = BlockchainSerializer()
    asset = AssetSerializer()

    class Meta:
        model = AssetOnBlockchain
        fields = ['id', 'address', 'blockchain', 'asset']


class WalletWithAssetOnBlockchainSerializerForWalletSerializer(serializers.ModelSerializer):
    asset_on_blockchain = AssetOnBlockchainSerializerForWalletWithAssetOnBlockchainSerializerForWalletSerializer()
    balance = serializers.SerializerMethodField()

    class Meta:
        model = WalletWithAssetOnBlockchain
        fields = ['id', 'asset_on_blockchain', 'balance']

    def get_balance(self, instance: WalletWithAssetOnBlockchain):
        return WalletHistoryWithAssetOnBlockchainSerializer(instance.history.last(), many=False).data


class WalletSerializer(serializers.ModelSerializer):
    assets_on_blockchains = WalletWithAssetOnBlockchainSerializerForWalletSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'name', 'address', 'assets_on_blockchains']


class BalanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceHistory
        fields = ['timestamp', 'balance']


class ProviderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderHistory
        fields = ['start_timestamp', 'end_timestamp', 'error']


class ProviderSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    last_run = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = ['name', 'path', 'status', 'configuration', 'last_run']

    def get_last_run(self, instance: Provider):
        return ProviderHistorySerializer(instance.history.last(), many=False).data
