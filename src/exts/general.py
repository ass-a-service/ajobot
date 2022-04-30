from disnake import CommandInteraction, User
from disnake.ext.commands import Bot, Cog, Context, command, is_owner, slash_command

from src.impl.bot import Bot


class General(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(name="support", description="Get an invite link to the support server.")
    async def support(self, itr: CommandInteraction) -> None:
        await itr.send("Here's an invite to my support server: /dev/null", ephemeral=True)

def setup(bot: Bot) -> None:
    bot.add_cog(General(bot))
