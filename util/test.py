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
    result = r.evalsha('14ad935184344bc46e4a73f6c51e93d27b26b6ee', '3', "ajobus-inventory", "lb", "468516898309537792:inventory", "468516898309537792", seed_1)
    print(f"{i}: {result}")
    i = i+1