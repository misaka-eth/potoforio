import datetime

import pytz

from core.models import Blockchain, Asset, Wallet, AssetOnBlockchain, BalanceHistory, Provider
from core.serializers import BlockchainSerializer, AssetSerializer, WalletSerializer, \
    AssetOnBlockchainSerializer, BalanceHistorySerializer, ProviderSerializer
from rest_framework import generics
from rest_framework.exceptions import ValidationError


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
    serializer_class = BalanceHistorySerializer

    def get_queryset(self):
        start_timestamp = self.request.GET.get('start_timestamp')
        start_timestamp = self._parse_start_timestamp(start_timestamp)

        return BalanceHistory.objects.filter(timestamp__gte=start_timestamp)

    @staticmethod
    def _parse_start_timestamp(start_timestamp):
        # convert to datetime
        try:
            start_timestamp = int(start_timestamp) // 1000
            return datetime.datetime.fromtimestamp(start_timestamp, tz=pytz.UTC)
        except Exception:
            raise ValidationError(f'Can not parse {start_timestamp} as timestamp string')


class ProviderListAPIView(generics.ListAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
