import os


os.environ.setdefault("APP_SECRET_KEY", "test-only-key-not-used-by-the-server")

from .settings import *  # noqa: E402,F403


SECRET_KEY = "test-only-key-not-used-by-the-server"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
