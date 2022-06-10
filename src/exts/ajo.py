from disnake import CommandInteraction, Message, User
from disnake.ext.commands import Cog, Context, Param, command, slash_command

from src.impl.bot import Bot

AJO = "🧄"

class Ajo(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.guild is None:
            return

        contains_ajo = await self.bot.manager.contains_ajo(message)

        # Relevant message
        if contains_ajo:
            # 1. Log the message into the timeseries redis
            # Hotfix
            vampire_key = f"{message.author.id}:vampire"
            vampire_level = self.bot.manager.redis.get(vampire_key) or 1
            vampire_level = int(vampire_level) # TODO: Fixme
            if vampire_level > 69:
                return

            # Log the guild +1 ajo message
            self.bot.manager.redis_ts.add(f"ajoseries:{message.guild.id}:{message.author.id}", int(message.created_at.timestamp()), 1, labels={"guild": message.guild.id, "author": message.author.id})

            # 2. Process the message
            await self.bot.manager.add_ajo(
                message.author.id,
                f"{message.author.name}#{message.author.discriminator}",
                1
            )

            is_begging = await self.bot.manager.is_begging_for_ajo(message)
            if is_begging:
                await message.add_reaction(AJO)

    # AJO/VERAJO
    @command(name="ajo", description="Get your count of ajos.")
    async def ajo_command(self, ctx: Context[Bot]) -> None:
        count = await self.bot.manager.get_ajo(ctx.author.id)
        await ctx.reply(f"{AJO} You have {count} ajos {AJO}")

    @slash_command(name="ajo", description="Get your count of ajos.")
    async def ajo(self, itr: CommandInteraction) -> None:
        count = await self.bot.manager.get_ajo(itr.author.id)
        await itr.send(f"{AJO} You have {count} ajos {AJO}")

    @command(name="verajo", description="See someone else's ajos.")
    async def verajo_command(self, ctx: Context[Bot], user: User) -> None:
        count = await self.bot.manager.get_ajo(user.id)
        await ctx.reply(f"{AJO} {user} has {count} ajos {AJO}")

    @slash_command(name="verajo", description="See someone else's ajos.")
    async def verajo(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to get the ajo count from.")
    ) -> None:
        count = await self.bot.manager.get_ajo(user.id)
        await itr.send(f"{AJO} {user} has {count} ajos {AJO}")

    # LEADERBOARD
    @command(name="leaderboard", description="Get the ajo leaderboard.")
    async def leaderboard_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(embed=await self.bot.manager.get_leaderboard())

    @slash_command(name="leaderboard", description="Get the ajo leaderboard.")
    async def leaderboard(self, itr: CommandInteraction) -> None:
        await itr.send(embed=await self.bot.manager.get_leaderboard())

    # GAMBLE
    async def __gamble(self, user: User, amount: str) -> str:
        return await self.bot.manager.gamble_ajo(user.id, amount)

    @command(name="gamble", description="Gamble your ajos.")
    async def gamble_command(self, ctx: Context[Bot], amount: str) -> None:
        await ctx.reply(await self.__gamble(ctx.author, amount))

    @slash_command(name="gamble", description="Gamble your ajos.")
    async def gamble(
        self,
        itr: CommandInteraction,
        amount: str = Param(description="How much ajos to gamble.")
    ) -> None:
        await itr.send(await self.__gamble(itr.author, amount))

    # PAY
    async def __pay(self, from_user: User, to_user: User, amount: int) -> str:
        reply = await self.bot.manager.pay_ajo(from_user.id, to_user.id, amount)
        return reply.replace("[[TO_USER]]", f"{to_user}")


    @command(name="pay", description="Pay someone ajos.")
    async def pay_command(self, ctx: Context[Bot], user: User, amount: int) -> None:
        await ctx.reply(await self.__pay(ctx.author, user, amount))

    @slash_command(name="pay", description="Pay someone ajos.")
    async def pay(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to pay."),
        amount: int = Param(description="The amount to pay."),
    ) -> None:
        await itr.send(await self.__pay(itr.author, user, amount))

    # WEEKLY CLAIM
    async def __weekly(self, user: User) -> str:
        return await self.bot.manager.claim_weekly(user.id)

    @command(name="weekly", description="Claim your weekly ajos.")
    async def weekly_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(await self.__weekly(ctx.author))

    @slash_command(name="weekly", description="Claim your weekly ajos.")
    async def weekly(self, itr: CommandInteraction) -> None:
        await itr.send(await self.__weekly(itr.author))

    # DAILY CLAIM
    async def __daily(self, user: User) -> str:
        return await self.bot.manager.claim_daily(user.id)

    @command(name="daily", description="Claim your daily ajos.")
    async def daily_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(await self.__daily(ctx.author))

    @slash_command(name="daily", description="Claim your daily ajos.")
    async def daily(self, itr: CommandInteraction) -> None:
        await itr.send(await self.__daily(itr.author))

    # DISCOMBOBULATE
    async def __discombobulate(self, from_user: User, to_user: User, amount: int) -> str:
        reply = await self.bot.manager.discombobulate(from_user.id, to_user.id, amount)
        return reply.replace("[[TO_USER]]", f"{to_user}")

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

    # ROULETTE
    async def __roulette(self) -> str:
        return await self.bot.manager.roulette()

    @command(name="roulette", description="Create a roulette")
    async def roulette_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(await self.__roulette())

    @slash_command(name="roulette", description="Create a roulette")
    async def roulette(self, itr: CommandInteraction) -> None:
        await itr.send(await self.__roulette())

    # ROULETTE SHOT
    async def __roulette_shot(self, user: User, roulette_id: str) -> str:
        return await self.bot.manager.roulette_shot(user.id, roulette_id)

    @command(name="roulette_shot", description="Try your luck")
    async def roulette_shot_command(self, ctx: Context[Bot], roulette_id: str) -> None:
        await ctx.reply(await self.__roulette_shot(ctx.author, roulette_id))

    @slash_command(name="roulette_shot", description="Try your luck")
    async def roulette_shot(
        self,
        itr: CommandInteraction,
        roulette_id: str = Param(description="The roulette id")
    ) -> None:
        await itr.send(await self.__roulette_shot(itr.author, roulette_id))

def setup(bot: Bot) -> None:
    bot.add_cog(Ajo(bot))
