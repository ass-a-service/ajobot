from disnake import CommandInteraction, Embed, Message
from disnake.ext.commands import Bot, Cog, slash_command
from ormar import NoMatch

from src.impl.database import Stats

GARLIC = "🧄"


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

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.guild is None:
            return

        if "garlic" in message.content.lower():
            await self._increment_user(message.author.id, str(message.author), 1)

    @slash_command(name="garlic", description="Get your garlic count.")
    async def garlic(self, itr: CommandInteraction) -> None:
        user = await self._resolve_user(itr.author.id, str(itr.author))

        await itr.send(f"{GARLIC} You have {user.count} garlic {GARLIC}")

    @slash_command(name="leaderboard", description="Get the garlic leaderboard.")
    async def leaderboard(self, itr: CommandInteraction) -> None:
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

        await itr.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Garlic())
