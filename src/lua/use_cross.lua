--! file: use_cross.lua
local inventory_key = KEYS[1]
local vampire_key = KEYS[2]

local item = ARGV[1]

-- ensure we actually own the item
local stack = tonumber(redis.call("hget", inventory_key, item))
if not stack or stack < 1 then
    return {"err", false}
end

-- use the item, decrease stack
redis.call("hdecrby", inventory_key, item, 1)

-- if there is no vampire, you just used the item
local vampire_level = tonumber(redis.call("get", vampire_key))
if not vampire_level or vampire_level < 1 then
    return {"OK", 0}
end

-- actually decrease stack and vampire level
local res = redis.call("decrby", vampire_key, 1)
return {"OK", res}
