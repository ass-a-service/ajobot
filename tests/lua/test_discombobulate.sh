#!/bin/sh
function test() {
    init1=$1
    init2=$2
    offer=$3

    echo ">>>>>>>>>>"
    redis-cli flushdb >/dev/null
    redis-cli zadd leaderboard $init1 lv $init2 axl >/dev/null

    redis-cli --eval ../../src/lua/discombobulate.lua leaderboard , lv axl $offer $(date +%N)

    echo ""

    echo "leaderboard:"
    redis-cli zrange leaderboard 0 -1 rev withscores
}

#test 100 100 33
#test 100 100 35
#test 100 100 100
#test 10 100 35
test 100 100 47.9
#test 100 100 -3
#test 100 100 -35.5
#test 100 100 foo
