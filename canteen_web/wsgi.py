"""Точка входа WSGI для сайта столовой."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "canteen_web.settings")
application = get_wsgi_application()
