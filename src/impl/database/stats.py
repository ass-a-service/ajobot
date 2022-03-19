# pyright: reportIncompatibleVariableOverride=false
# pyright: reportGeneralTypeIssues=false

from ormar import BigInteger, Model, String

from .metadata import database, metadata


class Stats(Model):
    class Meta:
        metadata = metadata
        database = database
        tablename = "stats"

    user: int = BigInteger(primary_key=True, autoincrement=False)
    name: str = String(max_length=255, nullable=False)
    count: int = BigInteger(default=0)
