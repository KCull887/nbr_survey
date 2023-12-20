from django.apps import AppConfig
from django.conf import settings

class MainConfig(AppConfig):
    name = 'main'

    # make sure that required custom settings are in place
    if not hasattr(settings, "VISIT_INFO_CUTOFF_DATE"):
        raise AttributeError("VISIT_INFO_CUTOFF_DATE is required in your Django settings.")
