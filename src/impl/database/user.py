# pyright: reportIncompatibleVariableOverride=false
# pyright: reportGeneralTypeIssues=false

from datetime import datetime

from ormar import BigInteger, DateTime, Model, String

from .metadata import database, metadata


class AjoUser(Model):
    class Meta:
        metadata = metadata
        database = database
        tablename = "stats"

    user: int = BigInteger(primary_key=True, autoincrement=False)
    name: str = String(max_length=255, nullable=False)
    count: int = BigInteger(default=0)
    last_daily: datetime = DateTime(nullable=True)
    last_weekly: datetime = DateTime(nullable=True)
