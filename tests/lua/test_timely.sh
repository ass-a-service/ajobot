#!/bin/sh
function test() {
    init=$1
    award=$2
    type=$3
    expire=$4
    init_ttl=$5

    echo ">>>>>>>>>>"
    redis-cli flushdb >/dev/null
    redis-cli zadd leaderboard $init lv >/dev/null
    if [ $init_ttl -ge 1 ]
    then
        redis-cli set lv:$type 1 >/dev/null
        redis-cli expire lv:$type $init_ttl >/dev/null
    fi

    redis-cli --eval ../../src/lua/timely_award.lua leaderboard lv:$type , lv $award $expire

    echo ""

    echo "leaderboard:"
    redis-cli zrange leaderboard 0 -1 rev withscores

    echo "ttl:"
    redis-cli ttl lv:$type
}

test 100 2000 daily 1337 0
test 100 4000 weekly 2498 0
test 100 4000 weekly 2498 10
