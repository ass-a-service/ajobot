from random import randrange, SystemRandom
from math import ceil, log

from disnake import Message, User
from disnake.ext.commands import Cog

from src.impl.bot import Bot

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

        # Depending on the vampire level of the user, it has more chance to be triggered
        vampire_level = self.bot.manager.redis.get(f"vampire:{message.author.id}") or 1
        vampire_level = int(vampire_level) # TODO: Fixme
        appear_chance = 1 if vampire_level == 1 else log(vampire_level,10)*20
        if appear_chance < SystemRandom().uniform(0,100):
            return

        ajo = await self.bot.manager.get_ajo(message.author.id)
        if ajo < 1:
            return

        # Depending on the vempire level of the user, it has more chance to hit harder
        min_damage = min(vampire_level*1.2,30)
        max_damage = min(40,vampire_level*2)
        random_pct = SystemRandom().uniform(min_damage,max_damage)
        to_pay = ceil(ajo * (random_pct/100))

        await self.bot.manager.add_ajo(
            message.author.id,
            f"{message.author.name}#{message.author.discriminator}",
            -to_pay
        )

        # Feature request: hay un 0.1% de que el vampiro te hace discombolulate y te jode y te quita un 33%.
        await message.reply(
            f"A vampire level {vampire_level} has appeared! You use {to_pay} ajos to defeat him. You are safe... for now."
        )

        # Vampire gets more aggresive for this user
        incr_by = 2 if vampire_level == 1 else 1
        self.bot.manager.redis.incrby(f"vampire:{message.author.id}",incr_by)
        self.bot.manager.redis.expire(f"vampire:{message.author.id}",min(7200, 600*vampire_level)) #TODO: Improve this 5 minutes thing


def setup(bot: Bot) -> None:
    bot.add_cog(Vampires(bot))
