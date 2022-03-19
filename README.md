# garlic-bot

Count your garlic stats!

You can blame Dragory for this exising :)

## Running the bot

To run the bot you will need Poetry, a database (MySQL, SQLite, Postgres, MariaDB), and optionally Redis. If Redis is not configured in your .env file the bot will use an in-memory fakeredis instance.

```sh
poetry install
DB_URI=<your db uri> poetry run alembic upgrade head
poetry run task start
```
