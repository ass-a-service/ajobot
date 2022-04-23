redis-cli -x script load < src/lua/*.lua

poetry run alembic upgrade head
poetry run task start
