"""
WSGI конфигурация для проекта.

Этот модуль содержит WSGI приложение, которое используется для
запуска проекта на WSGI-совместимых веб-серверах.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
