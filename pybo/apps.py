from django.apps import AppConfig
from .url_patterns import URLS

class PyboConfig(AppConfig):
    name = URLS['APP_NAME']
