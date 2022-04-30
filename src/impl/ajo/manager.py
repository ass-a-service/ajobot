from datetime import timedelta
from math import ceil
from random import randrange
from typing import Any, Protocol
from os import environ
import time

from disnake import Embed, Message
from loguru import logger
import redis

AJO = "🧄"
DAILY = 32
WEEKLY = DAILY * 8

DISCOMBOBULATE = "1b0cf976d8db4cb69ce54d60135a5e8fe1850607"
GAMBLE = "b55d79a6c9b2a3d3ce5a07aaf16fc6e68c8ab997"
PAY = "95813e7e3b61c064ecee01b59b637e72e5e03142"
TIMELY_AWARD = "997360eb43e1de043028dbf3556e1572d231e39e"
LEADERBOARD = "lb"

class AjoManager:
    def __init__(self) -> None:
        self.redis = redis.Redis(host=environ['REDIS_HOST'])
        logger.info("Connected to the database.")

    def _get_seed(self) -> int:
        return time.time_ns()

    async def contains_ajo(self, msg: Message) -> bool:
        txt = msg.content
        itxt = txt.lower()
        return "garlic" in itxt or "ajo" in itxt or AJO in txt or ":garlic" in txt

    async def is_begging_for_ajo(self, msg: Message) -> bool:
        itxt = msg.content.lower()
        return "give me garlic" in itxt or "dame ajo" in itxt

    async def add_ajo(self, user: str, amount: int) -> int:
        res = self.redis.zincrby(LEADERBOARD, amount, user)
        return int(res)

    async def get_ajo(self, user: str) -> int:
        res = self.redis.zscore(LEADERBOARD, user)
        if res is None:
            return 0
        return int(res)

    async def get_leaderboard(self) -> Embed:
        data = self.redis.zrange(LEADERBOARD, 0, 11, "rev", "withscores")
        embed = Embed(
            title="Ajo Leaderboard",
            colour=0x87CEEB,
        )

        j = 0
        for name, score in data:
            name = name.decode("utf-8")
            embed.add_field(
                name=f"{j} . {name[:-5]}",
                value=f"{AJO} {score:0.0f}",
                inline=True,
            )
            j += 1

        return embed

    async def gamble_ajo(self, user: str, amount: int) -> int:
        res = self.redis.evalsha(
            GAMBLE,
            1,
            LEADERBOARD,
            user,
            amount,
            self._get_seed()
        )
        if res is None:
            raise ValueError("You cannot gamble this amount.")
        return res

    async def pay_ajo(self, from_user: str, to_user: str, amount: int) -> None:
        res = self.redis.evalsha(
            PAY,
            1,
            LEADERBOARD,
            from_user,
            to_user,
            amount
        )
        if res is None:
            raise ValueError("You cannot pay this amount.")

        return res

    async def claim_daily(self, user: str) -> timedelta | None:
        res = self.redis.evalsha(
            TIMELY_AWARD,
            2,
            LEADERBOARD,
            (f"{user}:daily"),
            user,
            DAILY,
            24 * 3600
        )
        if res != b"OK":
            return timedelta(seconds=int(res))
        return None

    async def claim_weekly(self, user: str) -> timedelta | None:
        res = self.redis.evalsha(
            TIMELY_AWARD,
            2,
            LEADERBOARD,
            (f"{user}:weekly"),
            user,
            WEEKLY,
            7 * 24 * 3600
        )
        if res != b"OK":
            return timedelta(seconds=int(res))
        return None

    async def discombobulate(self, from_user: str, to_user: str, amount: int) -> None:
        res = self.redis.evalsha(
            DISCOMBOBULATE,
            1,
            LEADERBOARD,
            from_user,
            to_user,
            amount,
            self._get_seed()
        )
        if res is None:
            raise ValueError("You cannot discombobulate this amount.")

        return res
