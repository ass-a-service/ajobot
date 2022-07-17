from datetime import timedelta, datetime
from os import environ
import time
import secrets
from types import SimpleNamespace

from loguru import logger
import aioredis

AJO = "🧄"
CRUZ = '✝️'
CHOP = "🥢"

# timely rewards, type: [reward, expire_seconds]
TIMELY = {
    "daily": [32, 86400],
    "weekly": [256, 604800]
}

LEADERBOARD = "lb"
AJOBUS = "ajobus"
AJOBUS_INVENTORY = "ajobus-inventory"
EVENT_VERSION = 1

class AjoManager:
    def __init__(self) -> None:
        self.redis = aioredis.from_url(f"redis://{environ['REDIS_HOST']}")
        logger.info("Connected to the database.")

    def __translate_emoji(self, txt: str) -> str:
        match txt:
            case "chopsticks" | "🥢":
                txt = ":chopsticks:"
            case "cross" | "✝️":
                txt = ":cross:"
            case "ajo" | "garlic" | "🧄":
                txt = ":garlic:"
            case "ajo_necklace" | "🎗️":
                txt = ":reminder_ribbon:"
            case "herb" | "🌿":
                txt = ":herb:"
            case "bomb" | "💣":
                txt = ":bomb:"
            case "eggplant" | "🍆":
                txt = ":eggplant:"
            case "shoe" | "👟":
                txt = ":athletic_shoe:"
            case "wand" | "magic_wand" | "🪄":
                txt = ":magic_wand:"
            case "tooth" | "🦷":
                txt = ":tooth:"
            case "bone" | "🦴":
                txt = ":bone:"
            case "gear" | "⚙️":
                txt = ":gear:"
            case "satellite" | "📡":
                txt = ":satellite:"

        return txt

    async def contains_ajo(self, msg: str) -> bool:
        itxt = msg.lower()
        return "garlic" in itxt or "ajo" in itxt or AJO in msg or ":garlic" in msg

    async def is_begging_for_ajo(self, msg: str) -> bool:
        itxt = msg.lower()
        return "give me garlic" in itxt or "dame ajo" in itxt

    async def get_ajo(self, user_id: str) -> int:
        res = await self.redis.zscore(LEADERBOARD, user_id)
        if res is None:
            return 0
        return int(res)

    async def get_effects(self, user_id: str) -> dict:
        curse, buff = await self.redis.mget(
            f"{user_id}:wand-curse",
            f"{user_id}:discombobulate-buff"
        )

        res = {}
        if buff:
            res["Discombobulate buff"] = buff.decode("utf-8")

        if curse:
            res["Cursed"] = curse.decode("utf-8")

        return res

    async def get_leaderboard(self) -> dict:
        data = await self.redis.zrange(LEADERBOARD, 0, 9, "rev", "withscores")

        ids = []
        scores = []
        for id, score in data:
            ids.append(id.decode("utf-8"))
            scores.append(int(score))

        names = await self.redis.mget(ids)
        res = {}
        i = 0
        for i in range(len(names)):
            name = names[i].decode("utf-8")
            res[name] = scores[i]
            i += 1

        return res

    async def gamble_ajo(
        self,
        user_id: str,
        amount: str,
        guild_id: str
    ) -> str:
        err, res = await self.redis.evalsha(
            environ["gamble"],
            2,
            AJOBUS,
            LEADERBOARD,
            user_id,
            amount,
            EVENT_VERSION,
            guild_id
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
                    reply = f"{AJO} You lost {abs(change)} ajos. {AJO}"

        return reply

    async def pay_ajo(
        self,
        from_user_id: str,
        to_user_id: str,
        amount: int,
        guild_id: str
    ) -> str:
        err, res = await self.redis.evalsha(
            environ["pay"],
            2,
            AJOBUS,
            LEADERBOARD,
            from_user_id,
            to_user_id,
            amount,
            EVENT_VERSION,
            guild_id
        )

        match err.decode("utf-8"):
            case "err":
                reply = "You cannot pay this amount."
            case "futile":
                reply = "It is futile."
            case "funds":
                reply = "You do not have enough ajos to pay that much."
            case "OK":
                amount = int(res)
                reply = f"{AJO} You paid {amount} ajos to [[TO_USER]]. {AJO}"

        return reply

    async def __claim_timely(self, user_id: str, type: str, guild_id: str) -> str:
        exp_key = f"{user_id}:{type}"
        reward, expire = TIMELY[type]
        err, res = await self.redis.evalsha(
            environ["timely_reward"],
            3,
            AJOBUS,
            LEADERBOARD,
            exp_key,
            user_id,
            reward,
            expire,
            EVENT_VERSION,
            guild_id
        )

        match err.decode("utf-8"):
            case "ttl":
                td = timedelta(seconds=int(res))
                reply = f"You already claimed your {type} ajos, you can claim again in {td}."
            case "OK":
                reward = int(res)
                reply = f"{AJO} You claimed your {type} ajos! {AJO}"

        return reply

    async def claim_daily(self, user_id: int, guild_id: str) -> str:
        return await self.__claim_timely(user_id, "daily", guild_id)

    async def claim_weekly(self, user_id: int, guild_id: str) -> str:
        return await self.__claim_timely(user_id, "weekly", guild_id)

    async def discombobulate(
        self,
        from_user_id: str,
        to_user_id: str,
        amount: int,
        guild_id: str
    ) -> str:
        exp_key = f"{from_user_id}:discombobulate"
        buff_key = f"{from_user_id}:discombobulate-buff"
        err, res = await self.redis.evalsha(
            environ["discombobulate"],
            4,
            AJOBUS,
            LEADERBOARD,
            exp_key,
            buff_key,
            from_user_id,
            to_user_id,
            amount,
            EVENT_VERSION,
            guild_id
        )

        match err.decode("utf-8"):
            case "err":
                reply = "You cannot discombobulate this amount."
            case "futile":
                reply = "It is futile."
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

    async def roulette(self) -> str:
        roulette_id = secrets.token_hex(4)
        roulette_key = f"roulette:{roulette_id}"
        err, _ = await self.redis.evalsha(
            environ["roulette"],
            1,
            roulette_key,
            600
        )

        match err.decode("utf-8"):
            case "err":
                reply = f"Too many roulettes... {roulette_id}."
            case "OK":
                reply = f"{AJO} Roulette {roulette_id} created. {AJO}"

        return reply

    async def roulette_shot(self, user_id: str, roulette_id: str, guild_id: str) -> str:
        roulette_key = f"roulette:{roulette_id}"
        err, _ = await self.redis.evalsha(
            environ["roulette_shot"],
            3,
            AJOBUS,
            LEADERBOARD,
            roulette_key,
            user_id,
            EVENT_VERSION,
            guild_id
        )

        match err.decode("utf-8"):
            case "err":
                reply = "Not the roulette you are looking for."
            case "OK":
                reply = "You survived this shot."
            case "shot":
                reply = "Ded."

        return reply

    async def __build_inventory(self, items) -> dict:
        if not items:
            items = {}

        res = {}

        for item_name, item_amount in items:
            item_amount = int(item_amount)
            if item_amount > 0:
                res[item_name.decode()] = int(item_amount)


        return res

    async def get_inventory(self, user_id: str) -> dict:
        res = await self.redis.hgetall(f"{user_id}:inventory")
        return await self.__build_inventory(res.items())

    # same as get_inventory, but you pay for it
    async def see_inventory(self, from_user_id: str, to_user_id: str, guild_id: str) -> dict | str:
        inventory_key = f"{to_user_id}:inventory"

        err, res = await self.redis.evalsha(
            environ["see_inventory"],
            3,
            AJOBUS,
            LEADERBOARD,
            inventory_key,
            from_user_id,
            EVENT_VERSION,
            guild_id
        )

        match err.decode("utf-8"):
            case "funds":
                reply = f"This service is not free, {res} ajos required."
            case "OK":
                items = res[::2]
                quantities = res[1::2]
                return await self.__build_inventory(zip(items, quantities))

        return reply

    async def use_protection(self, user_id: str, item: str, guild_id: str) -> str:
        inventory_key = f"{user_id}:inventory"
        vampire_key = f"{user_id}:vampire"

        match item:
            case ":chopsticks:":
                script = "use_chopsticks"
            case ":cross:":
                script = "use_cross"

        err, res = await self.redis.evalsha(
            environ[script],
            3,
            AJOBUS_INVENTORY,
            inventory_key,
            vampire_key,
            user_id,
            item,
            EVENT_VERSION,
            guild_id
        )

        match err.decode("utf-8"):
            case "err":
                reply = f"You do not have enough {item}."
            case "OK":
                reply = f"You have used {item}, vampire level is now {res-1}."

        return reply

    async def use_shoe(self, user_id: str, item: str, guild_id: str) -> str:
        inventory_key = f"{user_id}:inventory"
        item_key = "items::athletic_shoe:"
        ajo_gain_key = f"{user_id}:ajo-gain"

        err = await self.redis.evalsha(
            environ["use_shoe"],
            4,
            AJOBUS_INVENTORY,
            inventory_key,
            item_key,
            ajo_gain_key,
            user_id,
            item,
            EVENT_VERSION,
            guild_id
        )

        match err.decode("utf-8"):
            case "err":
                reply = f"You do not have enough {item}."
            case "OK":
                reply = f"You have used {item}."

        return reply

    async def use_eggplant(self, user_id: str, item: str, guild_id: str) -> str:
        inventory_key = f"{user_id}:inventory"
        item_key = "items::eggplant:"
        buff_key = f"{user_id}:discombobulate-buff"

        err = await self.redis.evalsha(
            environ["use_eggplant"],
            4,
            AJOBUS_INVENTORY,
            inventory_key,
            item_key,
            buff_key,
            user_id,
            item,
            EVENT_VERSION,
            guild_id
        )

        match err.decode("utf-8"):
            case "err":
                reply = f"You do not have enough {item}."
            case "OK":
                reply = f"You have used {item}."

        return reply

    async def set_bomb(self, user_id: str, item: str, time: int, guild_id: str) -> str:
        inventory_key = f"{user_id}:inventory"
        item_key = "items::bomb:"

        err, res = await self.redis.evalsha(
            environ["set_bomb"],
            4,
            AJOBUS_INVENTORY,
            inventory_key,
            item_key,
            "ajocron-bomb",
            time,
            user_id,
            item,
            EVENT_VERSION,
            guild_id
        )

        ret = SimpleNamespace()

        match err.decode("utf-8"):
            case "err":
                ret.description = f"You do not have enough {item}."
                ret.title = "There was an error when setting up the bomb"
                ret.timestamp = None
            case "time":
                ret.timestamp = None
                ret.description = f"You cannot set a bomb at this time."
                ret.title = "There was an error when setting up the bomb"
            case "OK":
                ret.timestamp = datetime.fromtimestamp(res)
                ret.description = "Detonation time:"
                ret.title = "The bomb has been planted"
        return ret

    async def curse(self, user_id: str, item: str, target_id: str, guild_id: str) -> str:
        inventory_key = f"{user_id}:inventory"
        item_key = "items::magic_wand:"
        curse_key = f"{target_id}:wand-curse"

        err = await self.redis.evalsha(
            environ["curse"],
            4,
            AJOBUS_INVENTORY,
            inventory_key,
            item_key,
            curse_key,
            user_id,
            item,
            EVENT_VERSION,
            guild_id
        )

        match err.decode("utf-8"):
            case "err":
                reply = f"You do not have enough {item}."
            case "OK":
                reply = f"You have used {item}."

        return reply

    async def use(self, user_id: str, item: str, guild_id: str) -> str:
        # translate the emojis to redis compatible
        item = self.__translate_emoji(item)

        match item:
            case ":chopsticks:" | ":cross:":
                return await self.use_protection(user_id, item, guild_id)
            case ":athletic_shoe:":
                return await self.use_shoe(user_id, item, guild_id)
            case ":eggplant:":
                return await self.use_eggplant(user_id, item, guild_id)
            case ":satellite:":
                return await self.use_radar(user_id, item, guild_id)
            case _:
                return f"Unknown item {item}."

    async def trade(
        self,
        from_user_id: str,
        to_user_id: str,
        item: str,
        qty: int,
        guild_id: str
    ) -> str:
        # translate the emojis to redis compatible
        item = self.__translate_emoji(item)
        from_inventory_key = f"{from_user_id}:inventory"
        to_inventory_key = f"{to_user_id}:inventory"
        item_key = f"items:{item}"

        err, _ = await self.redis.evalsha(
            environ["trade"],
            4,
            AJOBUS_INVENTORY,
            from_inventory_key,
            to_inventory_key,
            item_key,
            from_user_id,
            to_user_id,
            item,
            qty,
            EVENT_VERSION,
            guild_id
        )

        match err.decode("utf-8"):
            case "unknown":
                reply = f"Unknown item {item}."
            case "tradable":
                reply = f"You cannot trade {item}."
            case "err" | "funds":
                reply = f"You do not have enough {item}."
            case "futile":
                reply = "It is futile."
            case "OK":
                reply = f"You have traded {item} to [[TO_USER]]."

        return reply

    async def craft(self, user_id: str, item: str, guild_id: str) -> str:
        inventory_key = f"{user_id}:inventory"

        # translate the emojis to redis compatible
        item = self.__translate_emoji(item)
        craft_key = f"craft:{item}"
        item_key = f"items:{item}"

        err, res = await self.redis.evalsha(
            environ["craft"],
            6,
            AJOBUS,
            AJOBUS_INVENTORY,
            LEADERBOARD,
            inventory_key,
            item_key,
            craft_key,
            item,
            user_id,
            EVENT_VERSION,
            guild_id
        )

        match err.decode("utf-8"):
            case "unknown":
                reply = f"Unknown item {item}."
            case "stack":
                reply = f"You cannot craft more {item}!"
            case "funds":
                currency = res[0].decode("utf-8")
                price = res[1]
                reply = f"You do not have enough materials, needs {price} {currency}."
            case "OK":
                reply = f"You have crafted {item} successfully."

        return reply

    async def use_radar(self, user_id: str, item: str, guild_id: str) -> dict | str:
        inventory_key = f"{user_id}:inventory"
        item_key = "items::satellite:"

        err, res = await self.redis.evalsha(
            environ["use_radar"],
            3,
            AJOBUS_INVENTORY,
            inventory_key,
            "ajocron-bomb",
            user_id,
            item,
            EVENT_VERSION,
            guild_id
        )

        if err.decode("utf-8") == "err":
            return f"You do not have enough {item}."

        if not res:
            return f"There are no active bombs."

        ids = res[::2]
        scores = res[1::2]
        names = await self.redis.mget(ids)

        # find names related with the ids
        j = 0
        now = int(time.time())
        res = {}
        for i in range(len(names)):
            name = names[i].decode("utf-8")
            when = int(scores[i].decode("utf-8"))

            res[f"{j} . {name[:-5]}"] = timedelta(seconds=when-now)

        return res
