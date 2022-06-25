--! file: use_cross.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]
local vampire_key = KEYS[3]

local id = ARGV[1]
local item = ARGV[2]

local ttl_per_level = 600

-- ensure we actually own the item
local stack = tonumber(redis.call("hget", inventory_key, item))
if not stack or stack < 1 then
    return {"err", false}
end

-- use the item, decrease stack
redis.call("hincrby", inventory_key, item, -1)
redis.call("xadd", strm_key, "*", "user_id", id, "item", item, "quantity", -1)

-- if there is no vampire, you just used the item
local vampire_level = tonumber(redis.call("get", vampire_key))
if not vampire_level or vampire_level < 1 then
    return {"OK", 0}
end

-- reduce the vampire and refresh the ttl
local new_level = vampire_level - 1
local ttl = math.min(ttl_per_level * new_level, 7200)
local res = redis.call("set", vampire_key, new_level, "EX", ttl)

return {"OK", res}
