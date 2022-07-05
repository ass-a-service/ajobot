from disnake import CommandInteraction, Message, User, Guild
from disnake.ext.commands import Cog, Context, Param, command, slash_command
from disnake.ext import tasks
from redis.exceptions import ResponseError

from src.impl.bot import Bot
import time
from os import environ

AJO = "🧄"
LEADERBOARD = "lb"
EVENT_VERSION = 1

class Ajo(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.on_ajo.start()

    @tasks.loop(seconds=1)
    async def on_ajo(self) -> None:
        redis = self.bot.manager.redis

        # Create the xreadgroup once
        # TODO: better do this outside of this fn
        try:
            redis.xgroup_create("ajobus","ajo-python",0, mkstream=True)
        except ResponseError as e:
            if str(e) != "BUSYGROUP Consumer Group name already exists":
                raise e

        data = redis.xreadgroup("ajo-python","ajo.py",streams={"ajobus": ">"},count=100)
        # stream_name, chunk
        for _, chunk in data:
            # entry_id, entry_data
            for entry_id, entry_data in chunk:
                entry = await self.parseEntry(entry_data)
                if entry["type"] == "farm":
                    user_id = entry["user_id"]
                    redis.evalsha(
                        environ['farm_inventory'],
                        3,
                        "ajobus-inventory",
                        "drop-rate",
                        LEADERBOARD,
                        user_id + ":inventory",
                        user_id,
                        EVENT_VERSION,
                        entry["guild_id"],
                        entry_id,
                        time.time_ns()-(int(time.time())*1000000000)
                    )


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
            #self.bot.manager.redis_ts.add(f"ajoseries:{message.guild.id}:{message.author.id}", int(message.created_at.timestamp()), 1, labels={"guild": message.guild.id, "author": message.author.id})

            # 2. Process the message
            await self.bot.manager.add_ajo(
                message.author.id,
                f"{message.author.name}#{message.author.discriminator}",
                1
            )

            self.bot.manager.redis.xadd(
                "ajobus",
                {
                    "version": EVENT_VERSION,
                    "type": "farm",
                    "user_id": message.author.id,
                    "guild_id": message.guild.id,
                    "amount": 1
                },
                "*",
            )

            is_begging = await self.bot.manager.is_begging_for_ajo(message)
            if is_begging:
                await message.add_reaction(AJO)

    # util to decode a redis stream entry
    async def parseEntry(self, data):
        res = {}
        for key, value in data.items():
            res[key.decode("utf-8")] = value
        return res

    async def getGuildId(self, guild: Guild) -> str:
        return 0 if guild is None else str(guild.id)

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
    async def __gamble(self, user: User, amount: str, guild: Guild) -> str:
        return await self.bot.manager.gamble_ajo(
            user.id,
            amount,
            await self.getGuildId(guild)
        )

    @command(name="gamble", description="Gamble your ajos.")
    async def gamble_command(self, ctx: Context[Bot], amount: str) -> None:
        await ctx.reply(await self.__gamble(ctx.author, amount, ctx.guild))

    @slash_command(name="gamble", description="Gamble your ajos.")
    async def gamble(
        self,
        itr: CommandInteraction,
        amount: str = Param(description="How much ajos to gamble.")
    ) -> None:
        await itr.send(await self.__gamble(itr.author, amount, itr.guild))

    # PAY
    async def __pay(
        self,
        from_user: User,
        to_user: User,
        amount: int,
        guild: Guild
    ) -> str:
        reply = await self.bot.manager.pay_ajo(
            from_user.id,
            to_user.id,
            amount,
            await self.getGuildId(guild)
        )
        return reply.replace("[[TO_USER]]", f"{to_user}")


    @command(name="pay", description="Pay someone ajos.")
    async def pay_command(self, ctx: Context[Bot], user: User, amount: int) -> None:
        await ctx.reply(await self.__pay(ctx.author, user, amount, ctx.guild))

    @slash_command(name="pay", description="Pay someone ajos.")
    async def pay(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to pay."),
        amount: int = Param(description="The amount to pay."),
    ) -> None:
        await itr.send(await self.__pay(itr.author, user, amount, itr.guild))

    # WEEKLY CLAIM
    async def __weekly(self, user: User, guild: Guild) -> str:
        return await self.bot.manager.claim_weekly(
            user.id,
            await self.getGuildId(guild)
        )

    @command(name="weekly", description="Claim your weekly ajos.")
    async def weekly_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(await self.__weekly(ctx.author, ctx.guild))

    @slash_command(name="weekly", description="Claim your weekly ajos.")
    async def weekly(self, itr: CommandInteraction) -> None:
        await itr.send(await self.__weekly(itr.author, itr.guild))

    # DAILY CLAIM
    async def __daily(self, user: User, guild: Guild) -> str:
        return await self.bot.manager.claim_daily(
            user.id,
            await self.getGuildId(guild)
        )

    @command(name="daily", description="Claim your daily ajos.")
    async def daily_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(await self.__daily(ctx.author, ctx.guild))

    @slash_command(name="daily", description="Claim your daily ajos.")
    async def daily(self, itr: CommandInteraction) -> None:
        await itr.send(await self.__daily(itr.author, itr.guild))

    # DISCOMBOBULATE
    async def __discombobulate(
        self,
        from_user: User,
        to_user: User,
        amount: int,
        guild: Guild
    ) -> str:
        reply = await self.bot.manager.discombobulate(
            from_user.id,
            to_user.id,
            amount,
            await self.getGuildId(guild)
        )
        return reply.replace("[[TO_USER]]", f"{to_user}")

    @command(name="discombobulate", description="Discombobulate someone.")
    async def discombobulate_command(self, ctx: Context[Bot], user: User, amount: int) -> None:
        await ctx.reply(await self.__discombobulate(ctx.author, user, amount, ctx.guild))

    @slash_command(name="discombobulate", description="Discombobulate someone.")
    async def discombobulate(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to discombobulate."),
        amount: int = Param(description="The amount to offer."),
    ) -> None:
        await itr.send(await self.__discombobulate(itr.author, user, amount, itr.guild))

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
    async def __roulette_shot(self, user: User, roulette_id: str, guild: Guild) -> str:
        return await self.bot.manager.roulette_shot(
            user.id,
            roulette_id,
            await self.getGuildId(guild)
        )

    @command(name="roulette_shot", description="Try your luck")
    async def roulette_shot_command(self, ctx: Context[Bot], roulette_id: str) -> None:
        await ctx.reply(await self.__roulette_shot(ctx.author, roulette_id, ctx.guild))

    @slash_command(name="roulette_shot", description="Try your luck")
    async def roulette_shot(
        self,
        itr: CommandInteraction,
        roulette_id: str = Param(description="The roulette id")
    ) -> None:
        await itr.send(await self.__roulette_shot(itr.author, roulette_id, itr.guild))

    # INVENTORY
    @command(name="inventory", description="Get inventory.")
    async def inventory_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(embed = await self.bot.manager.get_inventory(ctx.author.id))

    @slash_command(name="inventory", description="Get inventory")
    async def inventory(
        self,
        itr: CommandInteraction,
    ) -> None:
        await itr.send(embed = await self.bot.manager.get_inventory(itr.author.id), ephemeral=True)

    @command(name="verinventory", description="See someone's inventory.")
    async def verinventory_command(self, ctx: Context[Bot], user: User) -> None:
        res = await self.bot.manager.see_inventory(
            ctx.author.id,
            user.id,
            await self.getGuildId(ctx.guild)
        )
        if isinstance(res, str):
            await ctx.reply(res)
        else:
            await ctx.reply(embed = res)

    @slash_command(name="verinventory", description="See someone's inventory.")
    async def verinventory(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to spy on.")
    ) -> None:
        res = await self.bot.manager.see_inventory(
            itr.author.id,
            user.id,
            await self.getGuildId(itr.guild)
        )
        if isinstance(res, str):
            await itr.send(res, ephemeral=True)
        else:
            await itr.send(embed = res, ephemeral=True)

    # INVENTORY USE
    async def __use(self, user: User, item: str, guild: Guild) -> str:
        return await self.bot.manager.use(
            user.id,
            item,
            await self.getGuildId(guild)
        )

    @command(name="use", description="Use an item from the inventory")
    async def use_command(self, ctx: Context[Bot], item: str) -> None:
        await ctx.reply(await self.__use(ctx.author, item, ctx.guild))

    @slash_command(name="use", description="Use an item from the inventory")
    async def use(
        self,
        itr: CommandInteraction,
        item: str = Param(description="The item to use")
    ) -> None:
        await itr.send(await self.__use(itr.author, item, itr.guild))

    # INVENTORY TRADE
    async def __trade(
        self,
        from_user: User,
        to_user: User,
        item: str,
        quantity: int,
        guild: Guild
    ) -> str:
        reply = await self.bot.manager.trade(
            from_user.id,
            to_user.id,
            item,
            quantity,
            await self.getGuildId(guild)
        )
        return reply.replace("[[TO_USER]]", f"{to_user}")

    @command(name="trade", description="Trade an item from the inventory")
    async def trade_command(
        self,
        ctx: Context[Bot],
        user: User,
        item: str,
        quantity: int
    ) -> None:
        await ctx.reply(await self.__trade(ctx.author, user, item, quantity, ctx.guild))

    @slash_command(name="trade", description="Trade an item from the inventory")
    async def trade(
        self,
        itr: CommandInteraction,
        user: User = Param(description="The user to trade to."),
        item: str = Param(description="The item to trade."),
        quantity: int = Param(description="The quantity to trade."),
    ) -> None:
        await itr.send(await self.__trade(itr.author, user, item, quantity, itr.guild))

    # Craft
    async def __craft(self, user: User, item: str, guild: Guild) -> str:
        return await self.bot.manager.craft(user.id, item, await self.getGuildId(guild))

    @command(name="craft", description="Craft an item")
    async def craft_command(self, ctx: Context[Bot], item: str) -> None:
        await ctx.reply(await self.__craft(ctx.author, item, ctx.guild))

    @slash_command(name="craft", description="Craft an item")
    async def craft(
        self,
        itr: CommandInteraction,
        item: str = Param(description="The item to craft")
    ) -> None:
        await itr.send(await self.__craft(itr.author, item, itr.guild))

def setup(bot: Bot) -> None:
    bot.add_cog(Ajo(bot))
