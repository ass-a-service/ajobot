--! discombobulate.lua
local lb_key = KEYS[1]
local exp_key = KEYS[2]
local steal_key = KEYS[3]

local from_name = ARGV[1]
local to_name = ARGV[2]
local ajos = math.ceil(tonumber(ARGV[3]))
local now = ARGV[4]
local id = ARGV[5]

-- sanity checks
if ajos < 1 then
    return {"err", false}
end

-- can we steal?
local ttl = tonumber(redis.call("ttl", exp_key))
if ttl > 0 then
  return {"ttl", ttl}
end

-- can we steal that much?
local to_current = tonumber(redis.call("zscore", lb_key, to_name))
if not to_current or to_current < ajos then
    return {"funds", false}
end

-- TODO: Review this math
time = now + ajos*100

-- Queue the steal action
redis.call("zadd", steal_key, time, '{"id":"'.. id ..'","args":["'.. from_name ..'","'.. to_name ..'"],"name":"steal"}')
return {"OK", true}
