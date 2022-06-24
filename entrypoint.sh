#!/bin/sh
discombobulate=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/discombobulate.lua)
gamble=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/gamble.lua)
pay=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/pay.lua)
timely=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/timely_reward.lua)
setne=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/setne.lua)
roulette=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/roulette.lua)
roulette_shot=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/roulette_shot.lua)
farm_inventory=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/farm_inventory.lua)
use_chopsticks=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/use_chopsticks.lua)
use_cross=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/use_cross.lua)


grep DISCOMBOBULATE_SHA .env 1>/dev/null|| echo "DISCOMBOBULATE_SHA=$discombobulate" >> .env
grep GAMBLE_SHA .env 1>/dev/null|| echo "GAMBLE_SHA=$gamble" >> .env
grep PAY_SHA .env 1>/dev/null|| echo "PAY_SHA=$pay" >> .env
grep TIMELY_SHA .env 1>/dev/null|| echo "TIMELY_SHA=$timely" >> .env
grep SETNE_SHA .env 1>/dev/null|| echo "SETNE_SHA=$setne" >> .env
grep ROULETTE_SHA .env 1>/dev/null|| echo "ROULETTE_SHA=$roulette" >> .env
grep ROULETTE_SHOT_SHA .env 1>/dev/null|| echo "ROULETTE_SHOT_SHA=$roulette_shot" >> .env
grep FARM_INVENTORY_SHA .env 1>/dev/null|| echo "FARM_INVENTORY_SHA=$farm_inventory" >> .env
grep USE_CHOPSTICKS_SHA .env 1>/dev/null|| echo "USE_CHOPSTICKS_SHA=$use_chopsticks" >> .env
grep USE_CROSS_SHA .env 1>/dev/null|| echo "USE_CROSS_SHA=$use_cross" >> .env

poetry run task start
