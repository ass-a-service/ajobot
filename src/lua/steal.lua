--! discombobulate.lua
local lb_key = KEYS[1]
local exp_key = KEYS[2]

local from_name = ARGV[1]
local to_name = ARGV[2]
local offer = math.ceil(tonumber(ARGV[3]))

-- sanity checks
if offer < 1 then
    return {"err", false}
end

-- can we steal?
local ttl = tonumber(redis.call("ttl", exp_key))
if ttl > 0 then
  return {"ttl", ttl}
end

-- can we steal that much?
local to_current = tonumber(redis.call("zscore", lb_key, to_name))
if not to_current or to_current < offer then
    return {"funds", false}
end

-- TODO: Implement the steal action
return {"OK", true}
