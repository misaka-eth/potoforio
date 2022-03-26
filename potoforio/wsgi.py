"""
WSGI config for potoforio project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from initial_data.initial_data import init_data
from .history_manager import history_manager
from .provider_manager import provider_manager

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'potoforio.settings')

application = get_wsgi_application()

init_data()
provider_manager()
history_manager()
