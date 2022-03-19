from os import environ

from disnake import AllowedMentions, Intents

from . import Bot


def main() -> None:
    test_guilds: list[int] | None = None

    if guild := environ.get("TEST_GUILD"):
        test_guilds = [int(guild)]

    intents = Intents.none()
    intents.messages = True

    bot = Bot(
        test_guilds=test_guilds,
        intents=intents,
        command_prefix="g/",
        help_command=None,
        allowed_mentions=AllowedMentions.none(),
    )

    for ext in ["src.exts.garlic"]:
        bot.load_extension(ext)

    bot.run(environ["TOKEN"])


main()
