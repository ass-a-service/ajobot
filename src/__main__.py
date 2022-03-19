from os import environ

from . import Bot


def main() -> None:
    test_guilds: list[int] | None = None

    if guild := environ.get("TEST_GUILD"):
        test_guilds = [int(guild)]

    bot = Bot(test_guilds=test_guilds)

    for ext in ["src.exts.garlic"]:
        bot.load_extension(ext)

    bot.run(environ["TOKEN"])


main()
