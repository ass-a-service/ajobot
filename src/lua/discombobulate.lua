--! discombobulate.lua
local lb_key = KEYS[1]

local from_name = ARGV[1]
local to_name = ARGV[2]
local offer = math.ceil(tonumber(ARGV[3]))
local seed = tonumber(ARGV[4])

local from_current = tonumber(redis.call("zscore", lb_key, from_name))
if not from_current or offer < 1 or from_current < offer then
  return nil
end

-- minimum offer is 35% of the victim
local to_current = tonumber(redis.call("zscore", lb_key, to_name))
if not to_current or offer < ((35 / 100) * to_current) then
    return nil
end

-- dmg is 69 to 200% of offered
math.randomseed(seed)
local dmg = math.floor(math.random(69, 200) / 100 * offer)

if to_current - dmg < 0 then
  dmg = to_current
end

redis.call("zincrby", lb_key, -offer, from_name)
redis.call("zincrby", lb_key, -dmg, to_name)

return dmg
