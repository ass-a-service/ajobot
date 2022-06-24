#!/usr/bin/env python3

import time, os, math
import redis

r = redis.Redis(host='127.0.0.1')

#r.flushdb(asynchronous=False)

i=0
while True:
    seed_1 = time.time_ns()-(int(time.time())*1000000000)
    #seed_2 = str(int.from_bytes(os.urandom(16), 'big'))
    #seed_3 = seed_1[::-1]
    result = r.evalsha('d185c435f3af6c86f61a8a80a14fa379a52770b4', '3', "ajobus-inventory", "lb", "468516898309537792:inventory", "468516898309537792", seed_1)
    print(f"{i}: {result}")
    i = i+1