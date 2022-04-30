from disnake import CommandInteraction, Message, User
from disnake.ext.commands import Cog, Context, Param, command, slash_command

from src.impl.bot import Bot

AJO = "🧄"

class Ajo(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def _get_user_id(self, user: User) -> str:
        return f"{user.name}#{user.discriminator}"

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.guild is None:
            return

        # this message is not interesting
        contains_ajo = await self.bot.manager.contains_ajo(message)
        if not contains_ajo:
            return

        if contains_ajo:
            await self.bot.manager.add_ajo(self._get_user_id(message.author), 1)

        is_begging = await self.bot.manager.is_begging_for_ajo(message)
        if is_begging:
            await message.add_reaction(AJO)

    @slash_command(name="verajo", description="See someone else's ajos.")
    async def verajo(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to get the ajo count from.")
    ) -> None:
        count = await self.bot.manager.get_ajo(self._get_user_id(user))

        await itr.send(f"{AJO} {user} has {count} ajos {AJO}")

    @slash_command(name="ajo", description="Get your count of ajos.")
    async def ajo(self, itr: CommandInteraction) -> None:
        count = await self.bot.manager.get_ajo(self._get_user_id(itr.author))

        await itr.send(f"{AJO} You have {count} ajos {AJO}")

    @slash_command(name="leaderboard", description="Get the ajo leaderboard.")
    async def leaderboard(self, itr: CommandInteraction) -> None:
        await itr.send(embed=await self.bot.manager.get_leaderboard())

    @slash_command(name="gamble", description="Gamble your ajos.")
    async def gamble(
        self, itr: CommandInteraction, amount: int = Param(description="How much ajos to gamble.")
    ) -> None:
        try:
            change = await self.bot.manager.gamble_ajo(self._get_user_id(itr.author), amount)
        except ValueError as e:
            await itr.send(e.args[0])
            return

        if change > 0:
            await itr.send(f"{AJO} You won {change:,} ajos {AJO}")
        else:
            await itr.send(f"{AJO} You lost {abs(change):,} ajos {AJO}")

    @slash_command(name="pay", description="Pay someone ajos.")
    async def pay(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to pay."),
        amount: int = Param(description="The amount to pay."),
    ) -> None:
        try:
            await self.bot.manager.pay_ajo(self._get_user_id(itr.author), self._get_user_id(user), amount)
        except ValueError as e:
            await itr.send(e.args[0])
            return

        await itr.send(f"{AJO} You paid {amount:,} ajos to {user} {AJO}")

    @slash_command(name="daily", description="Claim your daily ajos.")
    async def daily(self, itr: CommandInteraction) -> None:
        res = await self.bot.manager.claim_daily(self._get_user_id(itr.author))

        if res:
            await itr.send(f"You already claimed your daily ajos, you can claim again in {res}.")
            return

        await itr.send(f"{AJO} You claimed your daily ajos! {AJO}")

    @slash_command(name="weekly", description="Claim your weekly ajos.")
    async def weekly(self, itr: CommandInteraction) -> None:
        res = await self.bot.manager.claim_weekly(self._get_user_id(itr.author))

        if res:
            await itr.send(f"You already claimed your weekly ajos, you can claim again in {res}.")
            return

        await itr.send(f"{AJO} You claimed your weekly ajos! {AJO}")

    @command(name="verajo", description="See someone else's ajos.")
    async def verajo_command(self, ctx: Context[Bot], user: User) -> None:
        count = await self.bot.manager.get_ajo(self._get_user_id(user))

        await ctx.reply(f"{AJO} {user} has {count} ajos {AJO}")

    @command(name="ajo", description="Get your count of ajos.")
    async def ajo_command(self, ctx: Context[Bot]) -> None:
        count = await self.bot.manager.get_ajo(self._get_user_id(ctx.author))

        await ctx.reply(f"{AJO} You have {count} ajos {AJO}")

    @command(name="leaderboard", description="Get the ajo leaderboard.")
    async def leaderboard_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(embed=await self.bot.manager.get_leaderboard())

    @command(name="gamble", description="Gamble your ajos.")
    async def gamble_command(self, ctx: Context[Bot], amount: int) -> None:
        try:
            change = await self.bot.manager.gamble_ajo(self._get_user_id(ctx.author), amount)
        except ValueError as e:
            await ctx.reply(e.args[0])
            return

        if change > 0:
            await ctx.reply(f"{AJO} You won {change:,} ajos {AJO}")
        else:
            await ctx.reply(f"{AJO} You lost {abs(change):,} ajos {AJO}")

    @command(name="pay", description="Pay someone ajos.")
    async def pay_command(self, ctx: Context[Bot], user: User, amount: int) -> None:
        try:
            await self.bot.manager.pay_ajo(self._get_user_id(ctx.author), self._get_user_id(user), amount)
        except ValueError as e:
            await ctx.reply(e.args[0])
            return

        await ctx.reply(f"{AJO} You paid {amount:,} ajos to {user} {AJO}")

    @command(name="daily", description="Claim your daily ajos.")
    async def daily_command(self, ctx: Context[Bot]) -> None:
        res = await self.bot.manager.claim_daily(self._get_user_id(ctx.author))

        if res:
            await ctx.reply(f"You already claimed your daily ajos, you can claim again in {res}.")
            return

        await ctx.reply(f"{AJO} You claimed your daily ajos! {AJO}")

    @command(name="weekly", description="Claim your weekly ajos.")
    async def weekly_command(self, ctx: Context[Bot]) -> None:
        res = await self.bot.manager.claim_weekly(self._get_user_id(ctx.author))

        if res:
            await ctx.reply(f"You already claimed your weekly ajos, you can claim again in {res}.")
            return

        await ctx.reply(f"{AJO} You claimed your weekly ajos! {AJO}")

    @command(name="discombobulate", description="Discombobulate someone.")
    async def discombobulate_command(self, ctx: Context[Bot], user: User, amount: int) -> None:
        try:
            discombobulate_amount = await self.bot.manager.discombobulate(self._get_user_id(ctx.author), self._get_user_id(user), amount)
        except ValueError as e:
            await ctx.reply(e.args[0])
            return

        await ctx.reply(f"{AJO} You discombobulate {user} for {discombobulate_amount} damage. {AJO} https://i.imgur.com/f2SsEqU.gif")

    @slash_command(name="discombobulate", description="Discombobulate someone.")
    async def discombobulate(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to discombobulate."),
        amount: int = Param(description="The amount to offer."),
    ) -> None:
        try:
            discombobulate_amount = await self.bot.manager.discombobulate(self._get_user_id(itr.author), self._get_user_id(user), amount)
        except ValueError as e:
            await itr.send(e.args[0])
            return

        await itr.send(f"{AJO} You discombobulate {user} for {discombobulate_amount} damage. {AJO} https://i.imgur.com/f2SsEqU.gif")


def setup(bot: Bot) -> None:
    bot.add_cog(Ajo(bot))
