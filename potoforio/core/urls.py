from django.urls import path, include
from potoforio.core import views
from potoforio.potoforio.settings import DEBUG_TOOLBAR

urlpatterns = [
    path('blockchain/', views.BlockchainListCreateAPIView.as_view()),

    path('assets/', views.AssetListCreateAPIView.as_view()),

    path('nfts/', views.NFTListAPIView.as_view()),

    path('wallet/', views.WalletListCreateAPIView.as_view(), name='wallets'),
    path('wallet/<pk>', views.WalletRetrieveUpdateDestroyAPIView.as_view(), name='wallet'),

    path('history/', views.BalanceHistoryListAPIView.as_view()),

    path('providers/', views.ProviderListAPIView.as_view()),

    path('asset_on_blockchain/', views.AssetOnBlockchainListCreateAPIView.as_view()),
]

if DEBUG_TOOLBAR:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
