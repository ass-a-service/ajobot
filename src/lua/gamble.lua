--! file: gamble.lua
local lb_key = KEYS[1]

local id = ARGV[1]
local amount = math.ceil(tonumber(ARGV[2]))
local seed = tonumber(ARGV[3])

-- sanity checks
if amount < 1 then
    return {"err", false}
end

-- can we gamble that much?
local current = tonumber(redis.call("zscore", lb_key, id))
if not current or current < amount then
  return {"funds", false}
end

-- 25% chance to win up from 1% to 250%
local change
math.randomseed(seed)
if math.random(0, 3) == 1 then
  change = math.ceil(math.random(1, 100) / 40 * amount)
else
  change = -amount
end

redis.call("zincrby", lb_key, change, id)
return {"OK", change}
