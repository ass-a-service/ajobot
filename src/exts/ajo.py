from disnake import CommandInteraction, MessageInteraction, Message, User, Guild, Embed, ButtonStyle, Member
from disnake.ext.commands import Cog, Context, Param, command, slash_command
from disnake.ext import tasks
from disnake.ui import Button, View
from aioredis.exceptions import ResponseError
from loguru import logger

from src.impl.bot import Bot
import time
from os import environ

AJO = "🧄"
LEADERBOARD = "lb"
EVENT_VERSION = 1
AJOBUS = "ajobus"
AJOBUS_INVENTORY = "ajobus-inventory"

class CustomView(View):
    def __init__(self, member: Member):
        self.member = member
        super().__init__(timeout=180)

    async def interaction_check(self, inter: MessageInteraction) -> bool:
        if inter.author != self.member:
            await inter.response.send_message(content="You don't have permission to press this button.", ephemeral=True)
            return False
        return True

class Ajo(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.on_ajo.start()
        self.bomb_cron.start()

    @tasks.loop(seconds=10)
    async def bomb_cron(self) -> None:
        try:
            redis = self.bot.manager.redis

            # read keys not read yet, assume these are bombs
            tm = time.time()
            data = await redis.zrangebyscore("ajocron-bomb", "-inf", tm)

            # we only care about the last item, bombs at the same time overwrite
            if len(data):
                # setup the bomb flag with the related username
                user_id = data[-1]
                await redis.set("ajobomb", await redis.get(user_id))

                # cleanup the cron
                await redis.zremrangebyscore("ajocron-bomb", "-inf", tm)
        except:
            logger.error("There was an exception while running bomb_cron task. Retrying.")

    @tasks.loop(seconds=1)
    async def on_ajo(self) -> None:
        try:
            redis = self.bot.manager.redis

            # Create the xreadgroup once
            # TODO: better do this outside of this fn
            try:
                await redis.xgroup_create(AJOBUS,"ajo-python",0, mkstream=True)
            except ResponseError as e:
                if str(e) != "BUSYGROUP Consumer Group name already exists":
                    raise e

            data = await redis.xreadgroup("ajo-python","ajo.py",streams={AJOBUS: ">"},count=100)
            # stream_name, chunk
            for _, chunk in data:
                # entry_id, entry_data
                for entry_id, entry_data in chunk:
                    entry = await self.parseEntry(entry_data)
                    if entry["type"] == "farm":
                        user_id = entry["user_id"]
                        await redis.evalsha(
                            environ['farm_inventory'],
                            4,
                            AJOBUS_INVENTORY,
                            "drop-rate",
                            LEADERBOARD,
                            user_id + ":inventory",
                            user_id,
                            EVENT_VERSION,
                            entry["guild_id"],
                            entry_id,
                            time.time_ns()-(int(time.time())*1000000000)
                        )
                    elif entry["type"] == "discombobulatee":
                        target = self.bot.get_user(int(entry["user_id"]))
                        guild = self.bot.get_guild(int(entry["guild_id"]))
                        discombobulator = self.bot.get_user(int(entry["discombobulator_id"]))
                        await target.send(f"You have been discombobulated by {discombobulator.name}#{discombobulator.discriminator} from guild "+guild.name)


        except Exception as e:
            logger.error("There was an exception while running on_ajo task. Retrying.")


    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.guild is None:
            return

        contains_ajo = await self.bot.manager.contains_ajo(message.content)

        # Relevant message
        if contains_ajo:
            ajo_gain_key = f"{message.author.id}:ajo-gain"
            vampire_key = f"{message.author.id}:vampire"
            bomb_key = "ajobomb"
            err, res = await self.bot.manager.redis.evalsha(
                environ["ajo"],
                6,
                AJOBUS,
                LEADERBOARD,
                ajo_gain_key,
                vampire_key,
                message.author.id,
                bomb_key,
                message.author.id,
                f"{message.author.name}#{message.author.discriminator}",
                EVENT_VERSION,
                message.guild.id # farm always has a guild
            )

            match err.decode("utf-8"):
                case "err":
                    return
                case "bomb":
                    bomb_owner = res[0].decode("utf-8")
                    return await message.reply(f"{bomb_owner}'s bomb explodes! {res[1]} ajos have been burnt.")

            is_begging = await self.bot.manager.is_begging_for_ajo(message.content)
            if is_begging:
                await message.add_reaction(AJO)

    # util to decode a redis stream entry
    async def parseEntry(self, data):
        res = {}
        for key, value in data.items():
            res[key.decode("utf-8")] = value.decode("utf-8")
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

    async def __get_leaderboard(self, page: int = 1, items_per_page: int = 10) -> Embed:
        embed = Embed(
            title="Ajo Leaderboard",
            colour=0x87CEEB,
        )
        lb = await self.bot.manager.get_leaderboard(page)
        page_to = (page*items_per_page)-1
        page_from = page_to-9
        j = page_from
        for name,points in lb.items():
            embed.add_field(
                name=f"{j} . {name[:-5]}",
                value=f"{AJO} {points}",
                inline=True
            )
            j += 1

        return embed

    # LEADERBOARD
    @slash_command(name="leaderboard", description="Get the ajo leaderboard.")
    async def leaderboard(self, itr: CommandInteraction) -> None:
        itr.response.defer
        view = CustomView(itr.author)
        previous = Button(style=ButtonStyle.primary, label="Previous", emoji="⏪")
        next =  Button(style=ButtonStyle.primary, label="Next", emoji="⏩")
        view.add_item(previous)
        view.add_item(next)
        async def button_callback(button_inter: MessageInteraction):
            await itr.edit_original_response(embed=await self.__get_leaderboard(), view=view)
            try:
                await button_inter.send("") # Actually this is needed to prevent client showing "Interaction failed"
            except Exception:
                pass
        previous.callback = button_callback
        next.callback = button_callback
        await itr.send(
            embed=await self.__get_leaderboard(),
            view=view,
            ephemeral=False
        )

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

    async def __get_inventory(self, author_id = None, inventory = None) -> Embed:
        if not inventory:
            inventory = await self.bot.manager.get_inventory(author_id)
        embed = Embed(
            title="Inventory",
            colour=0x87CEEB,
        )
        for item_name, quantity in inventory.items():
            embed.add_field(
                name=item_name,
                value=quantity,
                inline=True
            )
        return embed

    # INVENTORY
    @command(name="inventory", description="Get inventory.")
    async def inventory_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(embed = await self.__get_inventory(author_id=ctx.author.id))

    @slash_command(name="inventory", description="Get inventory")
    async def inventory(
        self,
        itr: CommandInteraction,
    ) -> None:
        await itr.send(embed = await self.__get_inventory(author_id=itr.author.id), ephemeral=True)

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
            await ctx.reply(embed = await self.__get_inventory(inventory=res))

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
            await itr.send(embed = await self.__get_inventory(inventory=res), ephemeral=True)

    # INVENTORY USE
    async def __use(self, user: User, item: str, guild: Guild) -> dict | str:
        return await self.bot.manager.use(
            user.id,
            item,
            await self.getGuildId(guild)
        )

    @command(name="use", description="Use an item from the inventory")
    async def use_command(self, ctx: Context[Bot], item: str) -> None:
        res = await self.__use(ctx.author, item, ctx.guild)
        if isinstance(res, str):
            await ctx.reply(res)
        else:
            await ctx.reply(embed = await self.__build_use_embed(res))

    @slash_command(name="use", description="Use an item from the inventory")
    async def use(
        self,
        itr: CommandInteraction,
        item: str = Param(description="The item to use")
    ) -> None:
        res = await self.__use(itr.author, item, itr.guild)
        if isinstance(res, str):
            await itr.send(res, ephemeral=True)
        else:
            await itr.send(embed = await self.__build_use_embed(res), ephemeral=True)

    async def __set_bomb(self, user: User, time: int, guild: Guild) -> Embed:
        message = await self.bot.manager.set_bomb(
            user.id,
            ":bomb:",
            time,
            await self.getGuildId(guild)
        )

        return Embed(
            timestamp = message.timestamp,
            description=message.description,
            title=message.title
        )


    @command(name="set_bomb", description="Set a bomb timer")
    async def set_bomb_command(self, ctx: Context[Bot], time: int) -> None:
        await ctx.reply(embed=await self.__set_bomb(ctx.author, time, ctx.guild))

    @slash_command(name="set_bomb", description="Set a bomb timer")
    async def set_bomb(
        self,
        itr: CommandInteraction,
        time: int = Param(description="Seconds until the bomb explodes")
    ) -> None:
        await itr.send(ephemeral=True, embed=await self.__set_bomb(itr.author, time, itr.guild))

    async def __curse(self, user: User, target: User, guild: Guild) -> str:
        return await self.bot.manager.curse(
            user.id,
            ":magic_wand:",
            target.id,
            await self.getGuildId(guild)
        )

    @command(name="curse", description="Curse someone")
    async def curse_command(self, ctx: Context[Bot], target: User) -> None:
        await ctx.reply(await self.__curse(ctx.author, target, ctx.guild))

    @slash_command(name="curse", description="Curse someone")
    async def set_bomb(
        self,
        itr: CommandInteraction,
        target: User = Param(description="Target of the curse")
    ) -> None:
        await itr.send(await self.__curse(itr.author, target, itr.guild))

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

    # EFFECTS
    @command(name="effects", description="Show your effects")
    async def effects_command(self, ctx: Context[Bot]) -> None:
        embed = await self.__build_effects(await self.bot.manager.get_effects(ctx.author.id))
        await ctx.reply(embed=embed)

    @slash_command(name="effects", description="Show your effects")
    async def effects(self, itr: CommandInteraction) -> None:
        embed = await self.__build_effects(await self.bot.manager.get_effects(itr.author.id))
        await itr.send(embed=embed, ephemeral=True)

    async def __build_effects(self, data) -> Embed:
        embed = Embed(
            title="Ajo effects",
            colour=0x87CEEB,
        )

        for effect, value in data.items():
            embed.add_field(
                name=effect,
                value=value,
                inline=True
            )

        return embed

    async def __build_use_embed(self, data) -> Embed:
        embed = Embed(
            title="Ajo radar",
            colour=0x87CEEB,
        )

        for name, td in data.items():
            embed.add_field(
                name=name,
                value=td,
                inline=True
            )

        return embed

def setup(bot: Bot) -> None:
    bot.add_cog(Ajo(bot))
