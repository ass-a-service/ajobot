from disnake import CommandInteraction
from disnake.ext.commands import Cog, slash_command, command, is_owner, Context, Bot

from src.impl.bot import Bot
from src.impl.database import GarlicUser


class General(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(name="support", description="Get an invite link to the support server.")
    async def support(self, itr: CommandInteraction) -> None:
        await itr.send("Here's an invite to my support server: https://discord.gg/t5Bs4cXfv2", ephemeral=True)

    @command(name="debug")
    @is_owner()
    async def debug(self, ctx: Context[Bot]) -> None:
        dbg = "\n".join([
            f"DB users: {await GarlicUser.objects.count()}",
            f"Latency: {self.bot.latency * 1000:.2f}ms",
        ])

        await ctx.send(dbg)


def setup(bot: Bot) -> None:
    bot.add_cog(General(bot))
