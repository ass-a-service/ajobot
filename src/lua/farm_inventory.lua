--! file: farm_inventory.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]

local id = tonumber(ARGV[1])
local seed = tonumber(ARGV[2])

-- implement here the items to potentially earn
local item = ":cucumber:"
local gato = ":pouting_cat:"

-- 25% chance to win a item
math.randomseed(seed)
if math.random(0, 3) ~= 1 then
    return {"err", false}
end

local res = redis.call("hincrby", inventory_key, item, 1)
if math.random(0, 3) ~= 1 then
    redis.call("xadd", strm_key, "*", "user_id", id, "item", item, "quantity", 1)
else
    redis.call("xadd", strm_key, "*", "user_id", id, "item", gato, "quantity", 1)
end
return {"OK", {item, res}}
