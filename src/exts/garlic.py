from math import ceil
from random import randrange

from disnake import AllowedMentions, CommandInteraction, Embed, Message
from disnake.ext.commands import Bot, Cog, Context, Param, command, slash_command
from ormar import NoMatch

from src.impl.database import Stats

GARLIC = "🧄"
MENTIONS = AllowedMentions(replied_user=False)


class Garlic(Cog):
    def __init__(self) -> None:
        self._users: dict[int, Stats] = {}

    async def _resolve_user(self, id: int, name: str) -> Stats:
        if id not in self._users:
            try:
                self._users[id] = await Stats.objects.get(user=id)
            except NoMatch:
                self._users[id] = await Stats(user=id, name=name).save()

        return self._users[id]

    async def _increment_user(self, id: int, name: str, garlic: int) -> None:
        user = await self._resolve_user(id, name)

        self._users[id] = await user.update(count=user.count + garlic)

    async def _get_leaderboard(self) -> Embed:
        users = await Stats.objects.order_by("-count").limit(12).all()  # type: ignore

        embed = Embed(
            title="Garlic Leaderboard",
            colour=0x87CEEB,
        )

        for i, user in enumerate(users):
            embed.add_field(
                name=f"{i + 1}. {user.name}",
                value=f"{GARLIC} {user.count:,}",
                inline=True,
            )

        return embed

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.guild is None:
            return

        if "garlic" in message.content.lower() or GARLIC in message.content or ":garlic:" in message.content:
            await self._increment_user(message.author.id, str(message.author), 1)

        if "give me garlic" in message.content.lower():
            await message.add_reaction(GARLIC)

    @slash_command(name="garlic", description="Get your garlic count.")
    async def garlic(self, itr: CommandInteraction) -> None:
        user = await self._resolve_user(itr.author.id, str(itr.author))

        await itr.send(f"{GARLIC} You have {user.count} garlic {GARLIC}")

    @slash_command(name="leaderboard", description="Get the garlic leaderboard.")
    async def leaderboard(self, itr: CommandInteraction) -> None:
        await itr.send(embed=await self._get_leaderboard())

    @slash_command(name="gamble", description="Gamble your garlic.")
    async def gamble(
        self, itr: CommandInteraction, amount: int = Param(description="How much garlic to gamble.")
    ) -> None:
        user = await self._resolve_user(itr.author.id, str(itr.author))

        if amount > user.count:
            await itr.send(f"{GARLIC} You don't have that much garlic {GARLIC}")
            return

        if randrange(0, 3) == 1:
            new = ceil((randrange(0, 100) / 100) * amount)

            await self._increment_user(itr.author.id, str(itr.author), new)
            await itr.send(f"{GARLIC} You won {new} garlic {GARLIC}")
        else:
            await self._increment_user(itr.author.id, str(itr.author), -amount)
            await itr.send(f"{GARLIC} You lost {amount} garlic {GARLIC}")

    @command(name="garlic", description="Get your garlic count.")
    async def garlic_command(self, ctx: Context[Bot]) -> None:
        user = await self._resolve_user(ctx.author.id, str(ctx.author))

        await ctx.reply(f"{GARLIC} You have {user.count} garlic {GARLIC}", allowed_mentions=MENTIONS)

    @command(name="leaderboard", description="Get the garlic leaderboard.")
    async def leaderboard_command(self, ctx: Context[Bot]) -> None:
        await ctx.reply(embed=await self._get_leaderboard(), allowed_mentions=MENTIONS)

    @command(name="gamble", description="Gamble your garlic.")
    async def gamble_command(self, ctx: Context[Bot], amount: int) -> None:
        user = await self._resolve_user(ctx.author.id, str(ctx.author))

        if amount > user.count:
            await ctx.reply(f"{GARLIC} You don't have that much garlic {GARLIC}", allowed_mentions=MENTIONS)
            return

        if randrange(0, 3) == 1:
            new = ceil((randrange(0, 100) / 100) * amount)

            await self._increment_user(ctx.author.id, str(ctx.author), new)
            await ctx.reply(f"{GARLIC} You won {new} garlic {GARLIC}", allowed_mentions=MENTIONS)
        else:
            await self._increment_user(ctx.author.id, str(ctx.author), -amount)
            await ctx.reply(f"{GARLIC} You lost {amount} garlic {GARLIC}", allowed_mentions=MENTIONS)


def setup(bot: Bot) -> None:
    bot.add_cog(Garlic())
