from disnake import CommandInteraction, Message, User
from disnake.ext.commands import Cog, Context, Param, command, slash_command

from src.impl.bot import Bot

AJO = "🧄"

class Ajo(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def __get_user_id(self, user: User) -> str:
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
            await self.bot.manager.add_ajo(self.__get_user_id(message.author), 1)

        is_begging = await self.bot.manager.is_begging_for_ajo(message)
        if is_begging:
            await message.add_reaction(AJO)

    # AJO/VERAJO
    @command(name="ajo", description="Get your count of ajos.")
    async def ajo_command(self, ctx: Context[Bot]) -> None:
        count = await self.bot.manager.get_ajo(self.__get_user_id(ctx.author))
        await ctx.reply(f"{AJO} You have {count} ajos {AJO}")

    @slash_command(name="ajo", description="Get your count of ajos.")
    async def ajo(self, itr: CommandInteraction) -> None:
        count = await self.bot.manager.get_ajo(self.__get_user_id(itr.author))
        await itr.send(f"{AJO} You have {count} ajos {AJO}")

    @command(name="verajo", description="See someone else's ajos.")
    async def verajo_command(self, ctx: Context[Bot], user: User) -> None:
        count = await self.bot.manager.get_ajo(self.__get_user_id(user))
        await ctx.reply(f"{AJO} {user} has {count} ajos {AJO}")

    @slash_command(name="verajo", description="See someone else's ajos.")
    async def verajo(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to get the ajo count from.")
    ) -> None:
        count = await self.bot.manager.get_ajo(self.__get_user_id(user))
        await itr.send(f"{AJO} {user} has {count} ajos {AJO}")

    # LEADERBOARD
    @command(name="leaderboard", description="Get the ajo leaderboard.")
    async def leaderboard_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(embed=await self.bot.manager.get_leaderboard())

    @slash_command(name="leaderboard", description="Get the ajo leaderboard.")
    async def leaderboard(self, itr: CommandInteraction) -> None:
        await itr.send(embed=await self.bot.manager.get_leaderboard())

    # GAMBLE
    async def __gamble(self, user: User, amount: int) -> str:
        id = self.__get_user_id(user)
        return await self.bot.manager.gamble_ajo(id, amount)

    @command(name="gamble", description="Gamble your ajos.")
    async def gamble_command(self, ctx: Context[Bot], amount: int) -> None:
        await ctx.reply(await self.__gamble(ctx.author, amount))

    @slash_command(name="gamble", description="Gamble your ajos.")
    async def gamble(
        self,
        itr: CommandInteraction,
        amount: int = Param(description="How much ajos to gamble.")
    ) -> None:
        await itr.send(await self.__gamble(itr.author), amount)

    # PAY
    async def __pay(self, from_user: User, to_user: User, amount: int) -> str:
        from_id = self.__get_user_id(from_user)
        to_id = self.__get_user_id(to_user)
        return await self.bot.manager.pay_ajo(from_id, to_id, amount)

    @command(name="pay", description="Pay someone ajos.")
    async def pay_command(self, ctx: Context[Bot], user: User, amount: int) -> None:
        await ctx.reply(await self.__pay(ctx.author), user, amount)

    @slash_command(name="pay", description="Pay someone ajos.")
    async def pay(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to pay."),
        amount: int = Param(description="The amount to pay."),
    ) -> None:
        await itr.send(await self.__pay(itr.author), user, amount)

    # WEEKLY CLAIM
    async def __weekly(self, user: User) -> str:
        id = self.__get_user_id(user)
        return await self.bot.manager.claim_weekly(id)

    @command(name="weekly", description="Claim your weekly ajos.")
    async def weekly_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(await self.__weekly(ctx.author))

    @slash_command(name="weekly", description="Claim your weekly ajos.")
    async def weekly(self, itr: CommandInteraction) -> None:
        await itr.send(await self.__weekly(ctx.author))

    # DAILY CLAIM
    async def __daily(self, user: User) -> str:
        id = self.__get_user_id(user)
        return await self.bot.manager.claim_daily(id)

    @command(name="daily", description="Claim your daily ajos.")
    async def daily_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(await self.__daily(ctx.author))

    @slash_command(name="daily", description="Claim your daily ajos.")
    async def daily(self, itr: CommandInteraction) -> None:
        await itr.send(await self.__daily(ctx.author))

    # DISCOMBOBULATE
    async def __discombobulate(self, from_user: User, to_user: User, amount: int) -> str:
        from_id = self.__get_user_id(from_user)
        to_id = self.__get_user_id(to_user)
        return await self.bot.manager.discombobulate(from_id, to_id, amount)

    @command(name="discombobulate", description="Discombobulate someone.")
    async def discombobulate_command(self, ctx: Context[Bot], user: User, amount: int) -> None:
        await ctx.reply(await self.__discombobulate(ctx.author, user, amount))

    @slash_command(name="discombobulate", description="Discombobulate someone.")
    async def discombobulate(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to discombobulate."),
        amount: int = Param(description="The amount to offer."),
    ) -> None:
        await itr.send(await self.__discombobulate(itr.author, user, amount))

def setup(bot: Bot) -> None:
    bot.add_cog(Ajo(bot))
