--! file: farm_inventory.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]

local seed = tonumber(ARGV[1])

-- implement here the items to potentially earn
local item = "cucumber"

-- 25% chance to win a item
math.randomseed(seed)
if math.random(0, 3) ~= 1 then
    return {"err", false}
end

local res = redis.call("hincrby", inventory_key, 1, "item")
redis.call("xadd", strm_key, "*", "user_id", id, "item", item, "quantity", 1)
return {"OK", {item, res}}
