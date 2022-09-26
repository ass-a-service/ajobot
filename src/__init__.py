from os import environ
from dotenv import load_dotenv
import sentry_sdk

load_dotenv()

from .impl import Bot

__all__ = ("Bot",)

sentry_sdk.init(
    dsn=environ.get('SENTRY_DSN'),

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)