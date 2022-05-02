#!/bin/sh
discombobulate=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/discombobulate.lua)
gamble=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/gamble.lua)
pay=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/pay.lua)
timely=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/timely_reward.lua)

grep DISCOMBOBULATE_SHA .env 1>/dev/null|| echo "DISCOMBOBULATE_SHA=$discombobulate" >> .env
grep GAMBLE_SHA .env 1>/dev/null|| echo "GAMBLE_SHA=$gamble" >> .env
grep PAY_SHA .env 1>/dev/null|| echo "PAY_SHA=$pay" >> .env
grep TIMELY_SHA .env 1>/dev/null|| echo "TIMELY_SHA=$timely" >> .env

poetry run task start
