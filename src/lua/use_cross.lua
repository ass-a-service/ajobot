--! file: use_cross.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]
local vampire_key = KEYS[3]

local id = ARGV[1]
local item = ARGV[2]
local event_version = ARGV[3]
local guild_id = ARGV[4]

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
local next_level = 1
if not vampire_level then
    return {"OK", next_level}
end

-- FIXME: the legacy vampire system has a bug: we need to delete the key when
-- the current level is 2 or lower.
-- When the fix in feat/vampire-lua is merged, we can simply remove this if
if vampire_level <= 2 then
    redis.call("del", vampire_key)
else
    next_level = redis.call("decrby", vampire_key, 1)
end

return {"OK", res}
