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
    "discombobulate": environ['DISCOMBOBULATE_SHA'],
    "gamble": environ['GAMBLE_SHA'],
    "pay": environ['PAY_SHA'],
    "reward": environ['TIMELY_SHA'],
    "setne": environ['SETNE_SHA']
}

LEADERBOARD = "lb"

class AjoManager:
    def __init__(self) -> None:
        self.redis = redis.Redis(host=environ['REDIS_HOST'])
        self.redis_ts = redis.Redis(host=environ['REDIS_HOST']).ts()
        logger.info("Connected to the database.")

    def __get_seed(self) -> int:
        return time.time_ns()-(int(time.time())*1000000000)

    async def __setne_name(self, user_id: str, user_name: str) -> None:
        # ensure the name we have is correct
        self.redis.evalsha(
            SCRIPTS["setne"],
            1,
            user_id,
            user_name
        )

    async def contains_ajo(self, msg: Message) -> bool:
        txt = msg.content
        itxt = txt.lower()
        return "garlic" in itxt or "ajo" in itxt or AJO in txt or ":garlic" in txt

    async def is_begging_for_ajo(self, msg: Message) -> bool:
        itxt = msg.content.lower()
        return "give me garlic" in itxt or "dame ajo" in itxt

    # we only update a user's name if we give him an ajo
    async def add_ajo(self, user_id: str, user_name: str, amount: int) -> int:
        # ensure the name we have is correct
        await self.__setne_name(user_id, user_name)
        res = self.redis.zincrby(LEADERBOARD, amount, user_id)
        return int(res)

    async def get_ajo(self, user_id: str) -> int:
        res = self.redis.zscore(LEADERBOARD, user_id)
        if res is None:
            return 0
        return int(res)

    async def get_leaderboard(self) -> Embed:
        data = self.redis.zrange(LEADERBOARD, 0, 9, "rev", "withscores")
        embed = Embed(
            title="Ajo Leaderboard",
            colour=0x87CEEB,
        )

        ids = []
        scores = []
        for id, score in data:
            ids.append(id.decode("utf-8"))
            scores.append(int(score))

        names = self.redis.mget(ids)
        j = 0
        for i in range(len(names)):
            name = names[i].decode("utf-8")
            embed.add_field(
                name=f"{j} . {name[:-5]}",
                value=f"{AJO} {scores[i]}",
                inline=True,
            )
            j += 1

        return embed

    async def gamble_ajo(self, user_id: str, amount: str) -> str:
        if amount.isnumeric():
            amount = int(amount)
        elif amount == "all":
            amount = await self.get_ajo(user_id)
        else:
            amount = 0

        err, res = self.redis.evalsha(
            SCRIPTS["gamble"],
            1,
            LEADERBOARD,
            user_id,
            amount,
            self.__get_seed()
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

    async def pay_ajo(self, from_user_id: str, to_user_id: str, amount: int) -> str:
        err, res = self.redis.evalsha(
            SCRIPTS["pay"],
            1,
            LEADERBOARD,
            from_user_id,
            to_user_id,
            amount
        )

        match err.decode("utf-8"):
            case "err":
                reply = "You cannot pay this amount."
            case "funds":
                reply = "You do not have enough ajos to pay that much."
            case "OK":
                amount = int(res)
                reply = f"{AJO} You paid {amount} ajos to [[TO_USER]] {AJO}"

        return reply

    async def __claim_timely(self, user_id: str, type: str,) -> str:
        exp_key = f"{user_id}:{type}"
        reward, expire = TIMELY[type]
        err, res = self.redis.evalsha(
            SCRIPTS["reward"],
            2,
            LEADERBOARD,
            exp_key,
            user_id,
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

    async def claim_daily(self, user_id: int) -> str:
        return await self.__claim_timely(user_id, "daily")

    async def claim_weekly(self, user_id: int) -> str:
        return await self.__claim_timely(user_id, "weekly")

    async def discombobulate(self, from_user_id: str, to_user_id: str, amount: int) -> str:
        exp_key = f"{from_user_id}:discombobulate"
        err, res = self.redis.evalsha(
            SCRIPTS["discombobulate"],
            2,
            LEADERBOARD,
            exp_key,
            from_user_id,
            to_user_id,
            amount,
            self.__get_seed()
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
                reply = f"You have not offered enough ajos to discombobulate [[TO_USER]], needs {min_offer}."
            case "OK":
                dmg = int(res)
                reply = f"{AJO} You discombobulate [[TO_USER]] for {dmg} damage. {AJO}" \
                        "https://i.imgur.com/f2SsEqU.gif"

        return reply
