#!/bin/sh
set -euf

REDIS_HOST="${REDIS_HOST:-127.0.0.1}"

# load scripts into memory
PATHS="discombobulate gamble pay timely_reward roulette roulette_shot"
PATHS="${PATHS} farm_inventory use_chopsticks use_cross craft"
PATHS="${PATHS} trade see_inventory vampire ajo use_shoe use_eggplant"
PATHS="${PATHS} use_bomb"
for path in ${PATHS}; do
    sha=$(redis-cli -h ${REDIS_HOST} -x script load < src/lua/$path.lua)
    grep "$path=" .env > /dev/null 2>&1 || echo "$path=" >> .env
    sed -i "s/\($path\)=\(.\+\)\?/\1=$sha/" .env
done

# bootstrap item data
python bootstrap_items.py | redis-cli -h ${REDIS_HOST} --pipe >/dev/null

poetry run task start
