from disnake import CommandInteraction, User
from disnake.ext.commands import Bot, Cog, Context, command, is_owner, slash_command

from src.impl.bot import Bot
from src.impl.database import GarlicUser


class General(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(name="support", description="Get an invite link to the support server.")
    async def support(self, itr: CommandInteraction) -> None:
        await itr.send("Here's an invite to my support server: /dev/null", ephemeral=True)

    @command(name="debug")
    @is_owner()
    async def debug(self, ctx: Context[Bot]) -> None:
        dbg = "\n".join(
            [
                f"DB users: {await GarlicUser.objects.count()}",
                f"Latency: {self.bot.latency * 1000:.2f}ms",
            ]
        )

        await ctx.send(dbg)

    @command(name="setajo")
    @is_owner()
    async def setgarlic(self, ctx: Context[Bot], user: User, amount: int) -> None:
        await self.bot.manager.set_user_garlic(user, amount)

        await ctx.send(f"Set ajo for {user} to {amount}")


def setup(bot: Bot) -> None:
    bot.add_cog(General(bot))
