from disnake import CommandInteraction, Message
from disnake.ext.commands import Cog, Context, Param, command, slash_command

from src.impl.bot import Bot

GARLIC = "🧄"


class Garlic(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.guild is None:
            return

        if "garlic" in message.content.lower() or GARLIC in message.content or ":garlic:" in message.content:
            await self.bot.manager.add_user_garlic(message.author, 1)

        if "give me garlic" in message.content.lower():
            await message.add_reaction(GARLIC)

    @slash_command(name="garlic", description="Get your garlic count.")
    async def garlic(self, itr: CommandInteraction) -> None:
        count = await self.bot.manager.get_user_garlic(itr.author)

        await itr.send(f"{GARLIC} You have {count} garlic {GARLIC}")

    @slash_command(name="leaderboard", description="Get the garlic leaderboard.")
    async def leaderboard(self, itr: CommandInteraction) -> None:
        await itr.send(embed=await self.bot.manager.get_leaderboard())

    @slash_command(name="gamble", description="Gamble your garlic.")
    async def gamble(
        self, itr: CommandInteraction, amount: int = Param(description="How much garlic to gamble.")
    ) -> None:
        try:
            change = await self.bot.manager.gamble_garlic(itr.author, amount)
        except ValueError:
            await itr.send("You don't have enough garlic to gamble that much.")
            return

        if change > 0:
            await itr.send(f"{GARLIC} You won {change:,} garlic {GARLIC}")
        else:
            await itr.send(f"{GARLIC} You lost {abs(change):,} garlic {GARLIC}")

    @command(name="garlic", description="Get your garlic count.")
    async def garlic_command(self, ctx: Context[Bot]) -> None:
        count = await self.bot.manager.get_user_garlic(ctx.author)

        await ctx.reply(f"{GARLIC} You have {count} garlic {GARLIC}")

    @command(name="leaderboard", description="Get the garlic leaderboard.")
    async def leaderboard_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(embed=await self.bot.manager.get_leaderboard())

    @command(name="gamble", description="Gamble your garlic.")
    async def gamble_command(self, ctx: Context[Bot], amount: int) -> None:
        try:
            change = await self.bot.manager.gamble_garlic(ctx.author, amount)
        except ValueError:
            await ctx.reply("You don't have enough garlic to gamble that much.")
            return

        if change > 0:
            await ctx.reply(f"{GARLIC} You won {change:,} garlic {GARLIC}")
        else:
            await ctx.reply(f"{GARLIC} You lost {abs(change):,} garlic {GARLIC}")


def setup(bot: Bot) -> None:
    bot.add_cog(Garlic(bot))
