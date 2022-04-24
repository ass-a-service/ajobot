#!/bin/sh

#if [ -z ${REDIS_HOST} ]; then
#     echo -e "Redis host not defined, using local one"
#     export REDIS_HOST=localhost
#else
#    echo -e "Host is ${REDIS_HOST}"
#fi

#redis-cli -h ${REDIS_HOST} -x script load < src/lua/*.lua

poetry run alembic upgrade head
poetry run task start
