from typing import Any, Optional

from disnake.ext.commands import Bot as _Bot
from loguru import logger

from ajobot_manager.manager import AjoManager

from .status import StatusHeartbeater


class Bot(_Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)  # type: ignore

        self._status = StatusHeartbeater()
        self.manager = AjoManager()

    async def start(self, *args: Any, reconnect: bool = True, **kwargs: Any) -> None:

        self._status.run()

        await super().start(*args, reconnect=reconnect, **kwargs)

    async def on_connect(self) -> None:
        logger.info("Connected to the Discord Gateway.")

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        raise

    async def on_ready(self) -> None:
        logger.info(f"READY event received, connected as {self.user} with {len(self.guilds)} guilds.")

    async def on_guild_join(self, guild) -> None:
        logger.info(f"Guild {guild} added me. Realoading now.")
        self.reload = True

    def load_extension(self, name: str, *, package: Optional[str] = None) -> None:
        super().load_extension(name, package=package)

        logger.info(f"Loaded extension {name}.")
