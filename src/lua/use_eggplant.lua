--! file: use_eggplant.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]
local item_key = KEYS[3]
local buff_key = KEYS[4]

local id = ARGV[1]
local item = ARGV[2]
local event_version = ARGV[3]
local guild_id = ARGV[4]

-- ensure we actually own the item
local stack = tonumber(redis.call("hget", inventory_key, item))
if not stack or stack < 1 then
    return "err"
end

-- decrease stack
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

-- the eggplant sets up a buff, find its value and ttl
local item_data = redis.call("hmget", item_key, "buff", "ttl")
if not item_data then
    return "err"
end

local buff = tonumber(item_data[1])
local ttl = tonumber(item_data[2])
redis.call("set", buff_key, buff, "EX", ttl)
return "OK"
