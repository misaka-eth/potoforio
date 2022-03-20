from core.models import Blockchain, Token, Wallet, TokenOnBlockchain, BalanceHistory
from core.serializers import BlockchainSerializer, TokenSerializer, WalletSerializer, \
    TokenOnBlockchainSerializer, BalanceHistorySerializer
from rest_framework import generics


class BlockchainListCreateAPIView(generics.ListCreateAPIView):
    queryset = Blockchain.objects.all()
    serializer_class = BlockchainSerializer


class TokenListCreateAPIView(generics.ListCreateAPIView):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer


class WalletListCreateAPIView(generics.ListCreateAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class WalletRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class TokenOnBlockchainListCreateAPIView(generics.ListCreateAPIView):
    queryset = TokenOnBlockchain.objects.all()
    serializer_class = TokenOnBlockchainSerializer


class BalanceHistoryListAPIView(generics.ListAPIView):
    queryset = BalanceHistory.objects.all()
    serializer_class = BalanceHistorySerializer
