# garlic-bot

Count your garlic stats!

You can blame Dragory for this exising :)

## Invite the bot

[Invite](https://discord.com/api/oauth2/authorize?client_id=954718378755489852&permissions=265280&scope=bot%20applications.commands)

[Without permissions](https://discord.com/api/oauth2/authorize?client_id=954718378755489852&permissions=265280&scope=bot%20applications.commands)

## Running the bot

To run the bot you will need Poetry, a database (MySQL, SQLite, Postgres, MariaDB), and optionally Redis. If Redis is not configured in your .env file the bot will use an in-memory fakeredis instance.

```sh
poetry install
DB_URI=<your db uri> poetry run alembic upgrade head
poetry run task start
```
