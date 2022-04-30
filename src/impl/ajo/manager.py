from datetime import timedelta
from math import ceil
from os import environ
import time

from disnake import Embed, Message
from loguru import logger
import redis

AJO = "🧄"

# timely rewards, type: [reward, expire_seconds]
TIMELY = {
    "daily": [32, 86400],
    "weekly": [256, 604800]
}

# script sha values
SCRIPTS = {
    "discombobulate": "13f0e6f5a9768bc2127660700be717c59a8dbbd4",
    "gamble": "8be00b480d51d41cbc72ce9e99fb88c0a9724862",
    "pay": "a5555e9c5fb167e363d281b91a51aa7be100a61d",
    "reward": "671988c19058773e8baa73cfeda43e30f6cfe84f"
}

LEADERBOARD = "lb"

class AjoManager:
    def __init__(self) -> None:
        self.redis = redis.Redis(host=environ['REDIS_HOST'])
        logger.info("Connected to the database.")

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
            score = int(score)
            embed.add_field(
                name=f"{j} . {name[:-5]}",
                value=f"{AJO} {score}",
                inline=True,
            )
            j += 1

        return embed

    async def gamble_ajo(self, user: str, amount: int) -> str:
        err, res = self.redis.evalsha(
            SCRIPTS["gamble"],
            1,
            LEADERBOARD,
            user,
            amount,
            time.time_ns()
        )

        match err.decode("utf-8"):
            case "err":
                reply = "You cannot gamble this amount."
            case "funds":
                reply = "You do not have enough ajos to gamble that much."
            case "OK":
                change = int(res)
                if change > 0:
                    reply = f"{AJO} You won {change} ajos! {AJO}"
                else:
                    reply = f"{AJO} You lost {abs(change)} ajos {AJO}"

        return reply

    async def pay_ajo(self, from_user: str, to_user: str, amount: int) -> str:
        err, res = self.redis.evalsha(
            SCRIPTS["pay"],
            1,
            LEADERBOARD,
            from_user,
            to_user,
            amount
        )

        match err.decode("utf-8"):
            case "err":
                reply = "You cannot pay this amount."
            case "funds":
                reply = "You do not have enough ajos to pay that much."
            case "OK":
                reward = int(res)
                reply = f"{AJO} You claimed your {type} ajos! {AJO}"

        return reply

    async def __claim_timely(self, user: str, type: str,) -> str:
        exp_key = f"{user}:{type}"
        reward, expire = TIMELY[type]
        err, res = self.redis.evalsha(
            SCRIPTS["reward"],
            2,
            LEADERBOARD,
            exp_key,
            user,
            reward,
            expire
        )

        match err.decode("utf-8"):
            case "ttl":
                td = timedelta(seconds=int(res))
                reply = f"You already claimed your {type} ajos, you can claim again in {td}."
            case "OK":
                reward = int(res)
                reply = f"{AJO} You claimed your {type} ajos! {AJO}"

        return reply

    async def claim_daily(self, user: str) -> str:
        return await self.__claim_timely("daily")

    async def claim_weekly(self, user: str) -> timedelta | None:
        return await self.__claim_timely("weekly")

    async def discombobulate(self, from_user: str, to_user: str, amount: int) -> str:
        err, res = self.redis.evalsha(
            SCRIPTS["discombobulate"],
            1,
            LEADERBOARD,
            from_user,
            to_user,
            amount,
            time.time_ns()
        )

        match err.decode("utf-8"):
            case "err":
                reply = "You cannot discombobulate this amount."
            case "ttl":
                td = timedelta(seconds=int(res))
                reply = f"You cannot discombobulate yet, next in {td}."
            case "funds":
                reply = f"You do not have enough ajos to discombobulate that much."
            case "offer":
                min_offer = int(res)
                reply = f"You have not offered enough ajos to discombobulate @{to_user}, needs {min_offer}."
            case "OK":
                dmg = int(res)
                reply = f"{AJO} You discombobulate {from_user} for {dmg} damage. {AJO}" \
                        "https://i.imgur.com/f2SsEqU.gif"

        return reply
