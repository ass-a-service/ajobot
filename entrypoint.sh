#!/bin/sh
set -euf

REDIS_HOST="${REDIS_HOST:-127.0.0.1}"
PATHS="discombobulate gamble pay timely_reward setne roulette roulette_shot"
PATHS="${PATHS} farm_inventory use_chopsticks use_cross craft_ajo_necklace"
PATHS="${PATHS} trade see_inventory vampire"

for path in ${PATHS}; do
    sha=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/$path.lua)
    grep "$path=" .env > /dev/null 2>&1 || echo "$path=" >> .env
    sed -i "s/\($path\)=\(.\+\)\?/\1=$sha/" .env
done

poetry run task start
