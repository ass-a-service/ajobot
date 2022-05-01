--! discombobulate.lua
local lb_key = KEYS[1]
local exp_key = KEYS[2]

local from_name = ARGV[1]
local to_name = ARGV[2]
local offer = math.ceil(tonumber(ARGV[3]))
local seed = tonumber(ARGV[4])

-- sanity checks
if offer < 1 then
    return {"err", false}
end

-- can we discombobulate?
local ttl = tonumber(redis.call("ttl", exp_key))
if ttl > 0 then
  return {"ttl", ttl}
end

-- can we discombobulate that much?
local from_current = tonumber(redis.call("zscore", lb_key, from_name))
if not from_current or from_current < offer then
    return {"funds", false}
end

-- minimum offer is 35% of the victim
local to_current = tonumber(redis.call("zscore", lb_key, to_name))
local min_offer = math.ceil((35 / 100) * to_current)
if not to_current or offer < min_offer then
    return {"offer", min_offer}
end

-- dmg is 69 to 200% of offered
math.randomseed(seed)
local percent = math.random(69, 200)
local dmg = math.floor(percent / 100 * offer)
if to_current - dmg < 0 then
  dmg = to_current
end

-- lock for percentage done in hours
redis.call("zincrby", lb_key, -offer, from_name)
redis.call("zincrby", lb_key, -dmg, to_name)
redis.set("set", exp_key, 1, "ex", percent * 3600)
return {"OK", dmg}
