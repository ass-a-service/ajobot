--! file: farm_inventory.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]

local id = tonumber(ARGV[1])
local seed = tonumber(ARGV[2])

-- implement here the items to potentially earn
local chopsticks = ":chopsticks:"
local cross = ":cross:"
local item

-- destellos / linterna
math.randomseed(seed)
local rand = math.random(0, 100000)
if rand == 0 then
    item = ":sauropod:" -- easter egg. It's just a beautiful dinosaur.
elseif rand <= 5 then
    item = chopsticks -- resets your vampire level to 0
elseif rand <= 250 then
    item = cross -- decrements your vampire level by 1
elseif rand <= 300 then
    item = ":bomb:" -- plants a bomb and a) the next person that farms will get the bomb or b) after x minutes (seteable) the last person that farmed will take the damage.
elseif rand <= 500 then
    item = "\xf0\x9f\x91\x9f" -- You farm twice as much for 5 minutes.
else
    return {"err", false}
end

local res = redis.call("hincrby", inventory_key, item, 1)
redis.call("xadd", strm_key, "*", "user_id", id, "item", item, "quantity", 1)
return {"OK", {item, res}}
