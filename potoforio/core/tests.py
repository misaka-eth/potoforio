from django.test import TestCase
from .models import Wallet, Asset
import django
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class WalletTestCase(TestCase):
    def setUp(self):
        Wallet.objects.create(name="wallet_1", address="0x")

    def test_wallet_name_unique(self):
        try:
            Wallet.objects.create(name="11", address="11")
            Wallet.objects.create(name="11", address="12")
            assert False, "Crated wallet with not unique name"
        except django.db.utils.IntegrityError as error:
            pass

    def test_wallet_address_unique(self):
        try:
            Wallet.objects.create(name="21", address="21")
            Wallet.objects.create(name="21", address="21")
            assert False, "Crated wallet with not unique address"
        except django.db.utils.IntegrityError:
            pass


class WalletAPITestCase(APITestCase):
    def test_create_wallet(self):
        url = reverse('wallets')
        data = {'name': 'wallet', 'address': '0x'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Wallet.objects.count(), 1)
        self.assertEqual(Wallet.objects.get().name, 'wallet')
        self.assertEqual(Wallet.objects.get().address, '0x')

    def test_delete_wallet(self):
        # Create wallet
        wallet = Wallet.objects.create(name="wallet_1", address="0x")

        # Try to delete
        url = reverse('wallet', args=(wallet.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Wallet.objects.count(), 0)

    def test_update_wallet(self):
        # Create wallet
        wallet = Wallet.objects.create(name="wallet_1", address="0x")

        # Try to update wallet | Ok
        url = reverse('wallet', args=(wallet.id,))
        data = {'name': 'wallet', 'address': '0x'}
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Wallet.objects.count(), 1)
        self.assertEqual(Wallet.objects.get().name, 'wallet')
        self.assertEqual(Wallet.objects.get().address, '0x')

        #  Try to update wallet | with error
        url = reverse('wallet', args=(wallet.id,))
        data = {'name': '', 'address': '0x'}
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AssetTestCase(TestCase):
    def setUp(self):
        Asset.objects.create(name='Ether', ticker="ETH", decimals=18)

    def test_asset_ticker_unique(self):
        try:
            Asset.objects.create(name='Ether', ticker="ETH", decimals=18)
            Asset.objects.create(name='Ether2', ticker="ETH", decimals=18)
            assert False, "Crated asset with not unique ticker"
        except django.db.utils.IntegrityError:
            pass
