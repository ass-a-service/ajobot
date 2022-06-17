--! file: farm_inventory.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]

local id = tonumber(ARGV[1])
local seed = tonumber(ARGV[2])

-- implement here the items to potentially earn
local cucu = ":cucumber:"
local gato = ":pouting_cat:"

-- 25% chance to win a item
math.randomseed(seed)
local rand = math.random(0, 3)
if rand == 1 then
    item = cucu
elseif rand == 2 then
    item = gato
else
    return {"err", false}
end

local res = redis.call("hincrby", inventory_key, item, 1)
redis.call("xadd", strm_key, "*", "user_id", id, "item", item, "quantity", 1)
return {"OK", {item, res}}
