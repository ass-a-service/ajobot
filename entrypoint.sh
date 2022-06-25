#!/bin/sh
set -euf

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
trade=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/trade.lua)
see_inventory=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/see_inventory.lua)
craft=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/craft.lua)

grep "DISCOMBOBULATE_SHA=" .env > /dev/null 2>&1 || echo "DISCOMBOBULATE_SHA=" >> .env
grep "GAMBLE_SHA=" .env > /dev/null 2>&1 || echo "GAMBLE_SHA=" >> .env
grep "PAY_SHA=" .env > /dev/null 2>&1 || echo "PAY_SHA=" >> .env
grep "TIMELY_SHA=" .env > /dev/null 2>&1 || echo "TIMELY_SHA=" >> .env
grep "SETNE_SHA=" .env > /dev/null 2>&1 || echo "SETNE_SHA=" >> .env
grep "ROULETTE_SHA=" .env > /dev/null 2>&1 || echo "ROULETTE_SHA=" >> .env
grep "ROULETTE_SHOT_SHA=" .env > /dev/null 2>&1 || echo "ROULETTE_SHOT_SHA=" >> .env
grep "FARM_INVENTORY_SHA=" .env > /dev/null 2>&1 || echo "FARM_INVENTORY_SHA=" >> .env
grep "USE_CHOPSTICKS_SHA=" .env > /dev/null 2>&1 || echo "USE_CHOPSTICKS_SHA=" >> .env
grep "USE_CROSS_SHA=" .env > /dev/null 2>&1 || echo "USE_CROSS_SHA=" >> .env
grep "TRADE_SHA=" .env > /dev/null 2>&1 || echo "TRADE_SHA=" >> .env
grep "SEE_INVENTORY_SHA=" .env > /dev/null 2>&1 || echo "SEE_INVENTORY_SHA=" >> .env
grep "CRAFT_SHA=" .env > /dev/null 2>&1 || echo "CRAFT_SHA=" >> .env

grep "DISCOMBOBULATE_SHA=" .env > /dev/null 2>&1 || echo "DISCOMBOBULATE_SHA=" >> .env
grep "GAMBLE_SHA=" .env > /dev/null 2>&1 || echo "GAMBLE_SHA=" >> .env
grep "PAY_SHA=" .env > /dev/null 2>&1 || echo "PAY_SHA=" >> .env
grep "TIMELY_SHA=" .env > /dev/null 2>&1 || echo "TIMELY_SHA=" >> .env
grep "SETNE_SHA=" .env > /dev/null 2>&1 || echo "SETNE_SHA=" >> .env
grep "ROULETTE_SHA=" .env > /dev/null 2>&1 || echo "ROULETTE_SHA=" >> .env
grep "ROULETTE_SHOT_SHA=" .env > /dev/null 2>&1 || echo "ROULETTE_SHOT_SHA=" >> .env
grep "FARM_INVENTORY_SHA=" .env > /dev/null 2>&1 || echo "FARM_INVENTORY_SHA=" >> .env
grep "USE_CHOPSTICKS_SHA=" .env > /dev/null 2>&1 || echo "USE_CHOPSTICKS_SHA=" >> .env
grep "USE_CROSS_SHA=" .env > /dev/null 2>&1 || echo "USE_CROSS_SHA=" >> .env
grep "CRAFT_SHA=" .env > /dev/null 2>&1 || echo "CRAFT_SHA=" >> .env

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
sed -i "s/\(TRADE_SHA\)=\([a-z0-9]\+\)\?/\1=$trade/" .env
sed -i "s/\(SEE_INVENTORY_SHA\)=\([a-z0-9]\+\)\?/\1=$see_inventory/" .env
sed -i "s/\(CRAFT_SHA\)=\([a-z0-9]\+\)\?/\1=$craft/" .env

poetry run task start
