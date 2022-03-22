from core.models import Blockchain, Asset, Wallet, AssetOnBlockchain, BalanceHistory
from core.serializers import BlockchainSerializer, AssetSerializer, WalletSerializer, \
    AssetOnBlockchainSerializer, BalanceHistorySerializer
from rest_framework import generics


class BlockchainListCreateAPIView(generics.ListCreateAPIView):
    queryset = Blockchain.objects.all()
    serializer_class = BlockchainSerializer


class AssetListCreateAPIView(generics.ListCreateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class WalletListCreateAPIView(generics.ListCreateAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class WalletRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class AssetOnBlockchainListCreateAPIView(generics.ListCreateAPIView):
    queryset = AssetOnBlockchain.objects.all()
    serializer_class = AssetOnBlockchainSerializer


class BalanceHistoryListAPIView(generics.ListAPIView):
    queryset = BalanceHistory.objects.all()
    serializer_class = BalanceHistorySerializer
