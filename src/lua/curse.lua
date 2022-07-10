--! file: curse.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]
local item_key = KEYS[3]
local curse_key = KEYS[4]

local id = ARGV[1]
local item = ARGV[2]
local event_version = ARGV[3]
local guild_id = ARGV[4]

-- ensure we actually own the item
local stack = tonumber(redis.call("hget", inventory_key, item))
if not stack or stack < 1 then
    return "err"
end

-- the magic wand sets up a curse, find its value and ttl
local item_data = redis.call("hmget", item_key, "curse", "ttl")
if not item_data then
    return "err"
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

local curse = tonumber(item_data[1])
local ttl = tonumber(item_data[2])
redis.call("set", curse_key, curse, "EX", ttl)
return "OK"
