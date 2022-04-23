from datetime import datetime, timedelta
from math import ceil
from random import randrange
from typing import Any, Protocol

from disnake import Embed
from ormar import NoMatch

from ..database import GarlicUser

DAILY = 32
WEEKLY = DAILY * 8


class User(Protocol):
    id: int
    name: str
    discriminator: Any


class GarlicManager:
    def __init__(self) -> None:
        self._cache: dict[int, GarlicUser] = {}

    async def _resolve_user(self, user: User) -> GarlicUser:
        #if user.id not in self._cache:
        if True:
            try:
                self._cache[user.id] = await GarlicUser.objects.get(user=user.id)
            except NoMatch:
                self._cache[user.id] = await GarlicUser(user=user.id, name=f"{user.name}#{user.discriminator}").save()

        return self._cache[user.id]

    async def set_user_garlic(self, user: User, amount: int) -> GarlicUser:
        stats = await self._resolve_user(user)
        stats = await stats.update(count=amount)

        self._cache[user.id] = stats

        return stats

    async def get_user_garlic(self, user: User) -> int:
        stats = await self._resolve_user(user)

        return stats.count

    async def add_user_garlic(self, user: User, amount: int) -> GarlicUser:
        stats = await self._resolve_user(user)
        stats = await stats.update(count=stats.count + amount)

        self._cache[user.id] = stats

        return stats

    async def get_leaderboard(self) -> Embed:
        users = await GarlicUser.objects.order_by("-count").limit(12).all()  # type: ignore

        embed = Embed(
            title="Ajo Leaderboard",
            colour=0x87CEEB,
        )

        for i, user in enumerate(users):
            embed.add_field(
                name=f"{i + 1}. {user.name[:-5]}",
                value=f"🧄 {user.count:,}",
                inline=True,
            )

        return embed

    async def gamble_garlic(self, user: User, amount: int) -> int:
        stats = await self._resolve_user(user)

        if amount < 1:
            raise ValueError("You can't gamble less than 1 ajo.")

        if amount > stats.count:
            raise ValueError("You don't have enough ajos to gamble that much.")

        if randrange(0, 3) == 1:
            change = ceil((randrange(0, 100) / 40) * amount)
            new = stats.count + change
        else:
            change = -amount
            new = stats.count - amount

        await self.set_user_garlic(user, new)

        return change

    async def pay_garlic(self, from_user: User, to_user: User, amount: int) -> None:
        from_stats = await self._resolve_user(from_user)

        if amount < 1:
            raise ValueError("You can't pay less than 1 ajo.")

        if amount > from_stats.count:
            raise ValueError("You don't have enough ajos to pay that much.")

        await self.add_user_garlic(from_user, -amount)
        await self.add_user_garlic(to_user, amount)

    async def claim_daily(self, user: User) -> timedelta | None:
        stats = await self._resolve_user(user)

        if stats.last_daily is None or datetime.utcnow() - stats.last_daily > timedelta(days=1):
            stats = await stats.update(last_daily=datetime.utcnow(), count=stats.count + DAILY)
            self._cache[user.id] = stats
            return

        return (stats.last_daily + timedelta(days=1)) - datetime.utcnow()

    async def claim_weekly(self, user: User) -> timedelta | None:
        stats = await self._resolve_user(user)

        if stats.last_weekly is None or datetime.utcnow() - stats.last_weekly > timedelta(days=7):
            stats = await stats.update(last_weekly=datetime.utcnow(), count=stats.count + WEEKLY)
            self._cache[user.id] = stats
            return

        return (stats.last_weekly + timedelta(days=7)) - datetime.utcnow()

    async def discombobulate(self, from_user: User, to_user: User, amount: int) -> None:
        from_stats = await self._resolve_user(from_user)
        to_stats = await self._resolve_user(to_user)

        if amount < 1:
            raise ValueError("You can't discombobulate for less than 1 ajo.")

        if amount > from_stats.count:
            raise ValueError(f"You don't have enough ajos to discombobulate {to_stats.name}.")

        if amount <= (35/100) * to_stats.count:
            raise ValueError(f"You haven't offered enough ajos to discombobulate {to_stats.name}.")
        
        # Remove ajos from from_user
        await self.add_user_garlic(from_user, -amount)

        # DISCOMBOBULATE!
        discombobulate_pct = randrange(69,200) # Feature idea: do a normal distribution random
        discombobulate_dmg = round(amount * (discombobulate_pct / 100))

        # Corner case: over 9000 discombobulate
        if to_stats.count - discombobulate_dmg < 0:
            discombobulate_dmg = to_stats.count

        await self.add_user_garlic(to_user, -discombobulate_dmg)

        return discombobulate_dmg

    async def show_garlic(self, to_user: User) -> None:
        to_stats = await self._resolve_user(to_user)
        return to_stats.count
