from disnake import CommandInteraction
from disnake.ext.commands import Cog, slash_command
from os import environ

from src.impl.bot import Bot

class General(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(name="support", description="Get an invite link to the support server.")
    async def support(self, itr: CommandInteraction) -> None:
        await itr.send("Here's an invite to my support server: /dev/null", ephemeral=True)

    @slash_command(name="dame", description="Give movidas.")
    async def dame(self, itr: CommandInteraction, type: str, amount: int) -> None:
        if not "DEBUG" in environ or environ["DEBUG"] != "1":
            return await itr.send("mongo")

        match type:
            case "ajos":
                await self.bot.manager.redis.zadd("lb", {itr.author.id: amount})
                return await itr.send(f"Set ajos to {amount}")
            case "chop"|"bomb"|"cross"|"ribb"|"herb"|"sauro"|"eggplant"|"shoe"|"tooth"|"bone"|"magic_wand":
                inv_key = f"{itr.author.id}:inventory"
                it_type = self.__trans(type)
                if not it_type:
                    return await itr.send(f"unk item {type}")

                await self.bot.manager.redis.hset(inv_key, it_type, amount)
                return await itr.send(f"Set {it_type} to {amount}")
            case "vampire":
                vam_key = f"{itr.author.id}:vampire"
                await self.bot.manager.redis.set(vam_key, amount)
                return await itr.send(f"Set vampire to {amount}")

        await itr.send("Nothing")

    def __trans(self, it_type: str) -> str:
        match it_type:
            case "chop":
                return ":chopsticks:"
            case "bomb":
                return ":bomb:"
            case "cross":
                return ":cross:"
            case "ribb":
                return ":reminder_ribbon:"
            case "herb":
                return ":herb:"
            case "sauro":
                return ":sauro:"
            case "eggplant":
                return ":eggplant:"
            case "shoe":
                return ":athletic_shoe:"
            case "tooth":
                return ":tooth:"
            case "bone":
                return ":bone:"
            case "magic_wand":
                return ":magic_wand:"

        return ":void:"


def setup(bot: Bot) -> None:
    bot.add_cog(General(bot))
