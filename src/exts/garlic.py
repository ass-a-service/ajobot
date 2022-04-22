from disnake import CommandInteraction, Message, User
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

        if "garlic" in message.content.lower() or "ajo" in message.content.lower() or GARLIC in message.content or ":garlic:" in message.content:
            await self.bot.manager.add_user_garlic(message.author, 1)

        if "give me garlic" in message.content.lower() or "dame ajo" in message.content.lower():
            await message.add_reaction(GARLIC)

    @slash_command(name="ajo", description="Get your count of ajos.")
    async def garlic(self, itr: CommandInteraction) -> None:
        count = await self.bot.manager.get_user_garlic(itr.author)

        await itr.send(f"{GARLIC} You have {count} ajos {GARLIC}")

    @slash_command(name="leaderboard", description="Get the ajo leaderboard.")
    async def leaderboard(self, itr: CommandInteraction) -> None:
        await itr.send(embed=await self.bot.manager.get_leaderboard())

    @slash_command(name="gamble", description="Gamble your ajos.")
    async def gamble(
        self, itr: CommandInteraction, amount: int = Param(description="How much ajos to gamble.")
    ) -> None:
        try:
            change = await self.bot.manager.gamble_garlic(itr.author, amount)
        except ValueError as e:
            await itr.send(e.args[0])
            return

        if change > 0:
            await itr.send(f"{GARLIC} You won {change:,} ajos {GARLIC}")
        else:
            await itr.send(f"{GARLIC} You lost {abs(change):,} ajos {GARLIC}")

    @slash_command(name="pay", description="Pay someone ajos.")
    async def pay(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to pay."),
        amount: int = Param(description="The amount to pay."),
    ) -> None:
        try:
            await self.bot.manager.pay_garlic(itr.author, user, amount)
        except ValueError as e:
            await itr.send(e.args[0])
            return

        await itr.send(f"{GARLIC} You paid {amount:,} ajos to {user} {GARLIC}")

    @slash_command(name="daily", description="Claim your daily ajos.")
    async def daily(self, itr: CommandInteraction) -> None:
        res = await self.bot.manager.claim_daily(itr.author)

        if res:
            await itr.send("You already claimed your daily ajos.")
            return

        await itr.send(f"{GARLIC} You claimed your daily ajos! {GARLIC}")

    @slash_command(name="weekly", description="Claim your weekly ajos.")
    async def weekly(self, itr: CommandInteraction) -> None:
        res = await self.bot.manager.claim_weekly(itr.author)

        if res:
            await itr.send("You already claimed your weekly ajos.")
            return

        await itr.send(f"{GARLIC} You claimed your weekly ajos! {GARLIC}")

    @command(name="ajo", description="Get your count of ajos.")
    async def garlic_command(self, ctx: Context[Bot]) -> None:
        count = await self.bot.manager.get_user_garlic(ctx.author)

        await ctx.reply(f"{GARLIC} You have {count} ajos {GARLIC}")

    @command(name="leaderboard", description="Get the ajo leaderboard.")
    async def leaderboard_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(embed=await self.bot.manager.get_leaderboard())

    @command(name="gamble", description="Gamble your ajos.")
    async def gamble_command(self, ctx: Context[Bot], amount: int) -> None:
        try:
            change = await self.bot.manager.gamble_garlic(ctx.author, amount)
        except ValueError as e:
            await ctx.reply(e.args[0])
            return

        if change > 0:
            await ctx.reply(f"{GARLIC} You won {change:,} garlic {GARLIC}")
        else:
            await ctx.reply(f"{GARLIC} You lost {abs(change):,} garlic {GARLIC}")

    @command(name="pay", description="Pay someone ajos.")
    async def pay_command(self, ctx: Context[Bot], user: User, amount: int) -> None:
        try:
            await self.bot.manager.pay_garlic(ctx.author, user, amount)
        except ValueError as e:
            await ctx.reply(e.args[0])
            return

        await ctx.reply(f"{GARLIC} You paid {amount:,} ajos to {user} {GARLIC}")

    @command(name="daily", description="Claim your daily ajos.")
    async def daily_command(self, ctx: Context[Bot]) -> None:
        res = await self.bot.manager.claim_daily(ctx.author)

        if res:
            await ctx.reply("You already claimed your daily ajos.")
            return

        await ctx.reply(f"{GARLIC} You claimed your daily ajos! {GARLIC}")

    @command(name="weekly", description="Claim your weekly ajos.")
    async def weekly_command(self, ctx: Context[Bot]) -> None:
        res = await self.bot.manager.claim_weekly(ctx.author)

        if res:
            await ctx.reply("You already claimed your weekly ajos.")
            return

        await ctx.reply(f"{GARLIC} You claimed your weekly ajos! {GARLIC}")

    @command(name="discombobulate", description="Discombobulate someone.")
    async def discombobulate_command(self, ctx: Context[Bot], user: User, amount: int) -> None:
        try:
            discombobulate_amount = await self.bot.manager.discombobulate(ctx.author, user, amount)
        except ValueError as e:
            await ctx.reply(e.args[0])
            return

        await ctx.reply(f"{GARLIC} You discombobulate {user} for {discombobulate_amount} damage. {GARLIC}")

    @slash_command(name="discombobulate", description="Discombobulate someone.")
    async def discombobulate(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to discombobulate."),
        amount: int = Param(description="The amount to offer."),
    ) -> None:
        try:
            discombobulate_amount = await self.bot.manager.discombobulate(itr.author, user, amount)
        except ValueError as e:
            await itr.send(e.args[0])
            return

        await itr.send(f"{GARLIC} You discombobulate {user} for {discombobulate_amount} damage. {GARLIC}")

    @command(name="verajo", description="See someone else's ajos.")
    async def verajo_command(self, ctx: Context[Bot], user: User) -> None:
        count = await self.bot.manager.show_garlic(user)

        await ctx.reply(f"{GARLIC} {user} has {count} ajos {GARLIC}")

    @slash_command(name="verajo", description="See someone else's ajos.")
    async def verajo(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to get the ajo count from.")
    ) -> None:
        count = await self.bot.manager.show_garlic(user)

        await itr.send(f"{GARLIC} {user} has {count} ajos {GARLIC}")


def setup(bot: Bot) -> None:
    bot.add_cog(Garlic(bot))
