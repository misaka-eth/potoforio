import logging
import os
import importlib
import inspect
import asyncio
import threading
import datetime

import pytz

from providers import Provider

from core.models import Provider as ProviderModel
from core.models import ProviderHistory as ProviderHistoryModel

PROVIDERS_DIR = 'providers'
LOGGER = logging.getLogger(__name__)


def register():
    # Remove last active providers
    ProviderModel.unregister_all()

    # Load new providers
    providers = os.listdir(PROVIDERS_DIR)
    for provider in providers:
        if os.path.isdir(os.path.join(PROVIDERS_DIR, provider)):
            provider_path = f'providers.{provider}'

            # Load provider module
            module = importlib.import_module(provider_path)

            # Determine provider classes
            for attribute in dir(module):
                # Can be class, module, object
                stuff = getattr(module, attribute)

                # Check stuff is class and class is provider
                if inspect.isclass(stuff) and issubclass(stuff, Provider):
                    provider = ProviderModel.register(
                        name=stuff.__name__,
                        path=provider_path,
                        configuration=stuff.get_default_configuration()
                    )
                    LOGGER.info(f"Registered provider: {provider}")


async def async_runner(provider: Provider):
    timeout = provider.get_configuration('timeout')

    while True:
        start_time = datetime.datetime.now(tz=pytz.UTC)
        error = None

        # Run safe
        try:
            await provider.run()
        except Exception as err:
            error = err

        # Save result to history
        ProviderHistoryModel.objects.create(
            provider=ProviderModel.objects.filter(name=provider.__class__.__name__).first(),
            start_timestamp=start_time,
            error=error
        )

        # And sleep by conf time
        await asyncio.sleep(timeout)


def runner(providers):
    for provider in providers:
        subprocess = threading.Thread(target=asyncio.run, args=[async_runner(provider), ])
        subprocess.start()


def start():
    providers = ProviderModel.objects.all()
    provider_objs = []

    for provider in providers:
        # Load provider module
        module = importlib.import_module(provider.path)
        provider_class = getattr(module, provider.name)
        provider_obj = provider_class(configuration=provider.configuration)
        provider_objs.append(provider_obj)

    runner(provider_objs)


def provider_manager():
    register()
    start()
