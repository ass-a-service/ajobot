<?php

$sha = [
    "discombobulate" => "f172b6011d263063c58f4238e998ef736b443c02",
    "gamble" => "b55d79a6c9b2a3d3ce5a07aaf16fc6e68c8ab997",
    "pay" => "95813e7e3b61c064ecee01b59b637e72e5e03142",
    "timely_award" => "997360eb43e1de043028dbf3556e1572d231e39e"
];

function pretty(array $set): string {
    return json_encode($set);
}

function gamble_tests($sha): void {
    $set = [
        ["id" => 111, "name" => "Lv", "count" => 40]
    ];

    $lb_key = "leaderboard";
    $name = "Lv";
    $seed = 1337;

    $tests = [
        ["gamble" => -1, "expected" => "/^\(nil\)$/"],
        ["gamble" => -4.5, "expected" => "/^\(nil\)$/"],
        ["gamble" => 41, "expected" => "/^\(nil\)$/"],
        ["gamble" => "foo", "expected" => "/^\(error\) ERR Error running script/"],
        ["gamble" => 30, "expected" => "OK"],
        ["gamble" => 20, "expected" => "OK"],
        ["gamble" => 1, "expected" => "OK"],
        ["gamble" => 5.9, "expected" => "OK"],
    ];

    echo sprintf("Testing set: %s\n", pretty($set));
    $successes = [];
    $errors = [];
    foreach ($tests as $test) {
        seed_redis($set);

        $gamble = $test["gamble"];
        $expected = $test["expected"];

        // run command
        unset($out);
        $cmd = sprintf(
            //"redis-cli --no-raw --eval ./gamble.lua %s , %s %s %s",
            "redis-cli --no-raw evalsha $sha[gamble] 1 %s %s %s %s",
            $lb_key,
            $name,
            $gamble,
            $seed
        );
        $res = exec($cmd, $out);

        // determine test result
        $failure = 1;
        if ($expected === "OK") {
            // if we expect a gamble success, it must match (integer) XX
            if (preg_match("/^\(integer\) (-?[\d]+?)$/", $res, $matches)) {
                $change = intval($matches[1]);
                if ($change < 0) {
                    // the change is negative, must be equal to gamble
                   if ($change !== ceil($gamble)) {
                        $failure = 0;
                    }
                } else {
                    // the change is positive, must be greater than 0 and less
                    // than 250% of the gamble
                    $max_result = $gamble * 2.5;
                    if ($change > 0 && $change <= $max_result) {
                        $failure = 0;
                    }
                }
            }
        } elseif (preg_match($expected, $res)) {
            $failure = 0;
        }

        // verify in redis
        $redis_exp = $test["redis"] ?? null;
        if ($redis_exp) {
            exec("redis-cli $redis_exp[cmd]", $out);
            $count = 0;
            for ($i = 1, $l = count($out); $i < $l; ++$i) {
                if ($out[$i] != $redis_exp["res"][$i]) {
                    $failure = 1;
                }
                ++$count;
            }

            if ($count == 0) {
                $failure = 1;
            }

            if ($failure) {
                $redis_failure = json_encode($out) . " VS EXPECTED " . json_encode($redis_exp["res"]);
            }
        }

        // prepare output result
        $msg = sprintf(
            "%s gambling for \"%s\", lua raw result: [%s]",
            $name,
            $gamble,
            $res
        );
        if ($failure === 1) {
            $errors[] = sprintf("F %s\n%s", $msg, $cmd);
        } else {
            $successes[] = sprintf(". %s", $msg);
        }
    }

    echo sprintf(
        "Test result %d/%d (total: %d)\n\nSuccesses:\n%s\n\nErrors:\n%s\n",
        count($successes),
        count($errors),
        count($tests),
        implode("\n", $successes),
        implode("\n", $errors)
    );
}

function pay_tests($sha): void {
    $set = [
        ["id" => 111, "name" => "Lv", "count" => 40],
        ["id" => 222, "name" => "Axl", "count" => 40]
    ];

    $lb_key = "leaderboard";
    $name1 = "Lv";
    $name2 = "Axl";

    $tests = [
        ["pay" => -1, "expected" => "/^\(nil\)$/"],
        ["pay" => -1.5, "expected" => "/^\(nil\)$/"],
        ["pay" => 41, "expected" => "/^\(nil\)$/"],
        ["pay" => "foo", "expected" => "/^\(error\) ERR Error running script/"],
        ["pay" => 30, "expected" => "/^\"OK\"$/", "redis" => [
            "cmd" => "zmscore leaderboard Lv Axl",
            "res"  => ["\"OK\"", 10, 70]
        ]],
        ["pay" => 20, "expected" => "/^\"OK\"$/", "redis" => [
            "cmd" => "zmscore leaderboard Lv Axl",
            "res"  => ["\"OK\"", 20, 60]
        ]],
        ["pay" => 40, "expected" => "/^\"OK\"$/", "redis" => [
            "cmd" => "zmscore leaderboard Lv Axl",
            "res"  => ["\"OK\"", 0, 80]
        ]],
        ["pay" => 30.9, "expected" => "/^\"OK\"$/", "redis" => [
            "cmd" => "zmscore leaderboard Lv Axl",
            "res"  => ["\"OK\"", 9, 71]
        ]],
        ["pay" => 2.9, "expected" => "/^\"OK\"$/", "redis" => [
            "cmd" => "zmscore leaderboard Lv Axl",
            "res"  => ["\"OK\"", 37, 43]
        ]]
    ];

    echo sprintf("Testing set: %s\n", pretty($set));
    $successes = [];
    $errors = [];
    foreach ($tests as $test) {
        seed_redis($set);

        $pay = $test["pay"];
        $expected = $test["expected"];

        // run command
        unset($out);
        $cmd = sprintf(
            //"redis-cli --no-raw --eval ./pay.lua %s , %s %s %s",
            "redis-cli --no-raw evalsha $sha[pay] 1 %s %s %s %s",
            $lb_key,
            $name1,
            $name2,
            $pay
        );
        $res = exec($cmd, $out);

        // determine test result
        $failure = 1;
        if ($expected === "OK") {
            $failure = 1;
        } elseif (preg_match($expected, $res)) {
            $failure = 0;
        }

        // verify in redis
        $redis_exp = $test["redis"] ?? null;
        if ($redis_exp) {
            exec("redis-cli $redis_exp[cmd]", $out);
            $count = 0;
            for ($i = 1, $l = count($out); $i < $l; ++$i) {
                if ($out[$i] != $redis_exp["res"][$i]) {
                    $failure = 1;
                }
                ++$count;
            }

            if ($count == 0) {
                $failure = 1;
            }

            if ($failure) {
                $redis_failure = json_encode($out) . " VS EXPECTED " . json_encode($redis_exp["res"]);
            }
        }

        // prepare output result
        $msg = sprintf(
            "%s paying \"%s\" to %s, lua raw result: [%s]",
            $name1,
            $pay,
            $name2,
            $res
        );
        if ($failure === 1) {
            if (isset($redis_failure)) {
                $errors[] = sprintf("F %s\n%s\n%s", $msg, $cmd, $redis_failure);
            } else {
                $errors[] = sprintf("F %s\n%s", $msg, $cmd);
            }
        } else {
            $successes[] = sprintf(". %s", $msg);
        }
    }

    echo sprintf(
        "Test success %d/%d (errors: %d)\n\nSuccesses:\n%s\n\nErrors:\n%s\n",
        count($successes),
        count($tests),
        count($errors),
        implode("\n", $successes),
        implode("\n", $errors)
    );
}

function seed_redis(array $set): void {
    $lb_key = "leaderboard";

    // Warn: not safe for shell args
    $cmd = sprintf(
        "redis-cli flushdb && && redis-cli zadd $lb_key %s",
        implode(' ', $mset),
        implode(' ', $zadd)
    );
    $res = exec($cmd, $out);
    //echo sprintf("%s\n", $cmd);
    if ($res === false) {
        echo "Redis seed failure: " . var_export($out, true) . "\n";
        exit();
    }
}

gamble_tests($sha);
pay_tests($sha);
