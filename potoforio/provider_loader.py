import os
import time

import asyncio
import traceback
from threading import Thread
import inspect
import logging
from providers import PriceProvider, BalanceProvider

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger(__name__)


def start_price_provider(price_provider: PriceProvider.__class__):
    async def run_forever():
        client = price_provider()
        while True:
            try:
                await client.scan()
            except Exception as error:
                LOGGER.warning(f"Error occurred: {error}")
                traceback.print_tb(error.__traceback__)
            time.sleep(60)

    subprocess = Thread(target=asyncio.run, args=[run_forever(), ])
    subprocess.start()


def start_balance_provider(balance_provider: BalanceProvider.__class__):
    async def run_forever():
        client = balance_provider()
        while True:
            try:
                await client.scan_all_wallet()
            except Exception as error:
                LOGGER.warning(f"Error occurred: {error}")
                traceback.print_tb(error.__traceback__)
            time.sleep(60)

    subprocess = Thread(target=asyncio.run, args=[run_forever(), ])
    subprocess.start()


def start_provider(provider_modules):
    for provider_module in dir(provider_modules):
        provider_class = getattr(provider_modules, provider_module)
        if not inspect.isclass(provider_class):
            continue
        if issubclass(provider_class, PriceProvider):
            LOGGER.info(f"Found price provider: {provider_class}")
            start_price_provider(provider_class)
        if issubclass(provider_class, BalanceProvider):
            LOGGER.info(f"Found balance provider: {provider_class}")
            start_balance_provider(provider_class)


def load_plugins():
    providers_dir = 'providers'
    providers = os.listdir(providers_dir)
    providers_modules = __import__('providers')

    for provider in providers:
        if os.path.isdir(os.path.join(providers_dir, provider)):
            provider_path = f'providers.{provider}'
            LOGGER.info(f"Loading providers in: {provider_path}")

            __import__(f'providers.{provider}')

            provider_modules = getattr(providers_modules, provider)

            start_provider(provider_modules)
