"""Throwaway settings for offline `manage.py check` / template render tests.

Imports the real settings, then swaps Postgres for an in-memory SQLite so the
check runs with no DB server and no real .env credentials. NOT for serving.
"""
import os

os.environ.setdefault('SECRET_KEY', 'check-only-not-secret')
os.environ.setdefault('DB_PASSWORD', 'check')

from config.settings import *  # noqa: F401,F403

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
