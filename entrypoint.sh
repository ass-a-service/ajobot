#!/bin/sh
redis-cli -h ${REDIS_HOST} -x script load < src/lua/discombobulate.lua
redis-cli -h ${REDIS_HOST} -x script load < src/lua/gamble.lua
redis-cli -h ${REDIS_HOST} -x script load < src/lua/pay.lua
redis-cli -h ${REDIS_HOST} -x script load < src/lua/timely_award.lua

poetry run task start
