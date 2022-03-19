from math import ceil
from random import randrange
from typing import Any, Protocol

from disnake import Embed
from ormar import NoMatch

from ..database import Stats


class User(Protocol):
    id: int
    name: str
    discriminator: Any


class GarlicManager:
    def __init__(self) -> None:
        self._cache: dict[int, Stats] = {}

    async def _resolve_user(self, user: User) -> Stats:
        if user.id not in self._cache:
            try:
                self._cache[user.id] = await Stats.objects.get(user=user.id)
            except NoMatch:
                self._cache[user.id] = await Stats(user=user.id, name=f"{user.name}#{user.discriminator}").save()

        return self._cache[user.id]

    async def set_user_garlic(self, user: User, amount: int) -> Stats:
        stats = await self._resolve_user(user)

        return await stats.update(count=amount)

    async def get_user_garlic(self, user: User) -> int:
        stats = await self._resolve_user(user)

        return stats.count

    async def add_user_garlic(self, user: User, amount: int) -> Stats:
        stats = await self._resolve_user(user)

        return await stats.update(count=stats.count + amount)

    async def get_leaderboard(self) -> Embed:
        users = await Stats.objects.order_by("-count").limit(12).all()  # type: ignore

        embed = Embed(
            title="Garlic Leaderboard",
            colour=0x87CEEB,
        )

        for i, user in enumerate(users):
            embed.add_field(
                name=f"{i + 1}. {user.name}",
                value=f"🧄 {user.count:,}",
                inline=True,
            )

        return embed

    async def gamble_garlic(self, user: User, amount: int) -> int:
        stats = await self._resolve_user(user)

        if amount > stats.count:
            raise ValueError("You don't have enough garlic to gamble that much.")

        if randrange(0, 3) == 1:
            change = ceil((randrange(0, 100) / 100) * amount)
            new = stats.count + change
        else:
            change = -amount
            new = stats.count - amount

        await self.set_user_garlic(user, new)

        return change
