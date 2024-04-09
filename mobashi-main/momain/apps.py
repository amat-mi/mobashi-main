from django.apps import AppConfig


class MomainConfig(AppConfig):
    name = "momain"

    def ready(self):
        from . import signals
