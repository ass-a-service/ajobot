from typing import Any, Optional

from disnake.ext.commands import Bot as _Bot
from loguru import logger

from src.impl.database import database
from src.impl.garlic import GarlicManager

from .status import StatusHeartbeater


class Bot(_Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)  # type: ignore

        self._status = StatusHeartbeater()
        self.manager = GarlicManager()

    async def start(self, *args: Any, reconnect: bool = True, **kwargs: Any) -> None:
        logger.info("Connecting to the database...")

        await database.connect()

        logger.info("Connected to the database.")

        self._status.run()

        await super().start(*args, reconnect=reconnect, **kwargs)

    async def on_connect(self) -> None:
        logger.info("Connected to the Discord Gateway.")

    async def on_ready(self) -> None:
        logger.info(f"READY event received, connected as {self.user} with {len(self.guilds)} guilds.")

    def load_extension(self, name: str, *, package: Optional[str] = None) -> None:
        super().load_extension(name, package=package)

        logger.info(f"Loaded extension {name}.")
