from django.test import TestCase
from .models import Blockchain, Token, Wallet, TokenOnBlockchain, WalletWithTokenOnBlockchain


class WalletTokenBlockchain(TestCase):
    def test(self):
        blockchain_eth = Blockchain.objects.create(name="Ethereum")
        blockchain_bsc = Blockchain.objects.create(name="BSC")

        token_eth = Token.objects.create(name="ETH", ticker="ETH", decimals=18)
        token_weth = Token.objects.create(name="WETH", ticker="WETH", decimals=18)
        token_bnb = Token.objects.create(name="BNB", ticker="BNB", decimals=18)

        wallet_0x = Wallet.objects.create(name="Ethereum universal", address="0x")

        eth_on_eth = TokenOnBlockchain.objects.create(token=token_eth, blockchain=blockchain_eth, address="")
        bnb_on_eth = TokenOnBlockchain.objects.create(token=token_bnb, blockchain=blockchain_eth, address="0xB8c77482e45F1F44dE1745F52C74426C631bDD52")
        weth_on_eth = TokenOnBlockchain.objects.create(token=token_weth, blockchain=blockchain_eth, address="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

        bnb_on_bnb = TokenOnBlockchain.objects.create(token=token_bnb, blockchain=blockchain_bsc, address="")
        eth_on_bnb = TokenOnBlockchain.objects.create(token=token_eth, blockchain=blockchain_bsc, address="0x2170ed0880ac9a755fd29b2688956bd959f933f8")
        weth_on_bnb = TokenOnBlockchain.objects.create(token=token_weth, blockchain=blockchain_bsc, address="0x4DB5a66E937A9F4473fA95b1cAF1d1E1D62E29EA")

        wallet_0x_eth_on_eth = WalletWithTokenOnBlockchain(wallet=wallet_0x, token_on_blockchain=eth_on_eth)

