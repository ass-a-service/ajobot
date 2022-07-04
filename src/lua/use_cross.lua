--! file: use_cross.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]
local vampire_key = KEYS[3]

local id = ARGV[1]
local item = ARGV[2]
local event_version = ARGV[3]
local guild_id = ARGV[4]

local ttl_per_level = 600

-- ensure we actually own the item
local stack = tonumber(redis.call("hget", inventory_key, item))
if not stack or stack < 1 then
    return {"err", false}
end

-- use the item, decrease stack
redis.call("hincrby", inventory_key, item, -1)
redis.call(
    "xadd", strm_key, "*",
    "version", event_version,
    "type", "item_used",
    "user_id", id,
    "guild_id", guild_id,
    "item", item,
    "quantity", -1
)

-- the vampire level in redis is the level which will appear next, not current
local vampire_level = tonumber(redis.call("get", vampire_key))
if not vampire_level then
    return {"OK", 1}
end

-- reduce the vampire and refresh the ttl
local new_level = vampire_level - 1
local ttl = math.min(ttl_per_level * new_level, 7200)
redis.call("set", vampire_key, new_level, "EX", ttl)

return {"OK", new_level}
