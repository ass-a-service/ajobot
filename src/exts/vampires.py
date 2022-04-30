from random import randrange
from math import ceil

from disnake import Message, User
from disnake.ext.commands import Cog

from src.impl.bot import Bot

class Vampires(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def _get_user_id(self, user: User) -> str:
        return f"{user.name}#{user.discriminator}"

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.guild is None:
            return

        contains_ajo = await self.bot.manager.contains_ajo(message)
        if not contains_ajo:
            return

        if randrange(0, 100):
            return

        ajo = await self.bot.manager.get_ajo(self._get_user_id(message.author))
        if ajo < 1:
            return

        random_pct = randrange(1,10)
        to_pay = ceil(ajo * (random_pct/100))

        await self.bot.manager.add_ajo(self._get_user_id(message.author), -to_pay)
        # Feature request: hay un 0.1% de que el vampiro te hace discombolulate y te jode y te quita un 33%.
        await message.reply(
            f"A vampire has appeared! You use {to_pay} ajos to defeat them. You are safe... for now."
        )


def setup(bot: Bot) -> None:
    bot.add_cog(Vampires(bot))
