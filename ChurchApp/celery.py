from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
import logging

# Set default Django settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ChurchApp.settings")

app = Celery("ChurchApp")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

logger = logging.getLogger(__name__)

logger.info("Celery beat schedule updated")




