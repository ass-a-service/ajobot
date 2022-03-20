from random import randrange

from disnake import Message
from disnake.ext.commands import Cog

from src.impl.bot import Bot


class Vampires(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.guild is None:
            return

        if "garlic" in message.content.lower():
            if randrange(0, 150):
                return

            garlic = await self.bot.manager.get_user_garlic(message.author)

            if garlic < 1:
                return

            to_pay = round(garlic / 50) + 1

            await self.bot.manager.add_user_garlic(message.author, -to_pay)
            await message.reply(
                f"A vampire has appeared! You use {to_pay} garlic to defeat them. You are safe... for now."
            )


def setup(bot: Bot) -> None:
    bot.add_cog(Vampires(bot))
