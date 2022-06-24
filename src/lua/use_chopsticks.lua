--! file: use_chopsticks.lua
local inventory_key = KEYS[1]
local vampire_key = KEYS[2]

local item = ARGV[1]

-- ensure we actually own the item
local stack = tonumber(redis.call("hget", inventory_key, item))
if not stack or stack < 1 then
    return {"err", false}
end

-- decrease stack and vampire level
redis.call("hdecrby", inventory_key, item, 1)
local res = redis.call("del", vampire_key)
return {"OK", res}
