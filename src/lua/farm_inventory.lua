--! file: farm_inventory.lua

local strm_key = KEYS[1]
local inventory_key = KEYS[2]

local seed = tonumber(ARGV[1])

-- sanity checks

-- 25% chance to win a cucumber
math.randomseed(seed)
if math.random(0, 3) == 1 then
  local res = redis.call("zincrby", inventory_key, 1, ":cucumber:")
  local set = {cucumber=res} --TODO: Improve this hardcoded pickle..! Há!
  return {"OK", cjson.encode(set)}
  -- append data to stream
  -- TODO: redis.call("xadd", strm_key, "*", "user_id", id, "item", ":cucumber:", "amount", 1)
else
  return {"err", false}
end

