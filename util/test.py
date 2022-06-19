import time, os, math
import redis

r = redis.Redis(host='127.0.0.1')

#r.flushdb(asynchronous=False)

while True:
    seed_1 = str(time.time_ns()-(int(time.time())*1000000000))
    #seed_2 = str(int.from_bytes(os.urandom(16), 'big'))
    #seed_3 = seed_1[::-1]
    result = r.evalsha('7f391805f220372f55f2ed3652a5d10082d75750', '2', "ajobus-inventory", "468516898309537792:inventory", "78313426", seed_1)
    print(result)