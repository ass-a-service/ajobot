#!/bin/bash
set -euf -o pipefail

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
craft_ajo_necklace=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/craft_ajo_necklace.lua)

sed -i "s/\(DISCOMBOBULATE_SHA\)=\([a-z0-9]\+\)\?/\1=$discombobulate/" .env
sed -i "s/\(GAMBLE_SHA\)=\([a-z0-9]\+\)\?/\1=$gamble/" .env
sed -i "s/\(PAY_SHA\)=\([a-z0-9]\+\)\?/\1=$pay/" .env
sed -i "s/\(TIMELY_SHA\)=\([a-z0-9]\+\)\?/\1=$timely/" .env
sed -i "s/\(SETNE_SHA\)=\([a-z0-9]\+\)\?/\1=$setne/" .env
sed -i "s/\(ROULETTE_SHA\)=\([a-z0-9]\+\)\?/\1=$roulette/" .env
sed -i "s/\(ROULETTE_SHOT_SHA\)=\([a-z0-9]\+\)\?/\1=$roulette_shot/" .env
sed -i "s/\(FARM_INVENTORY_SHA\)=\([a-z0-9]\+\)\?/\1=$farm_inventory/" .env
sed -i "s/\(USE_CHOPSTICKS_SHA\)=\([a-z0-9]\+\)\?/\1=$use_chopsticks/" .env
sed -i "s/\(USE_CROSS_SHA\)=\([a-z0-9]\+\)\?/\1=$use_cross/" .env
sed -i "s/\(CRAFT_AJO_NECKLACE_SHA\)=\([a-z0-9]\+\)\?/\1=$craft_ajo_necklace/" .env

poetry run task start
