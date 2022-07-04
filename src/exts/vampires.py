from random import randrange, SystemRandom
from math import ceil, log
from os import environ
import time

from disnake import Message, User
from disnake.ext.commands import Cog

from src.impl.bot import Bot

LEADERBOARD = "lb"
AJOBUS = "ajobus"
EVENT_VERSION = 1

class Vampires(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.guild is None:
            return

        contains_ajo = await self.bot.manager.contains_ajo(message)
        if not contains_ajo:
            return

        vampire_key = f"{message.author.id}:vampire"
        _, res = self.bot.manager.redis.evalsha(
            environ["vampire"],
            3,
            AJOBUS,
            LEADERBOARD,
            vampire_key,
            message.author.id,
            EVENT_VERSION,
            0 if message.guild is None else message.guild.id,
            time.time_ns()-(int(time.time())*1000000000)
        )

        if not res:
            return

        await message.reply(
            f"A vampire level {res[0]} has appeared! You use {res[1]} ajos to defeat him. You are safe... for now."
        )

def setup(bot: Bot) -> None:
    bot.add_cog(Vampires(bot))
