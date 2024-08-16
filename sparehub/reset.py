import django
from django.apps import apps
from django.conf import settings

settings.configure()
django.setup()

apps.get_app_configs()
apps.clear_cache()