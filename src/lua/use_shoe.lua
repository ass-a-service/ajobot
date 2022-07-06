--! file: use_shoe.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]
local item_key = KEYS[3]
local ajo_gain_key = KEYS[4]

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

-- the shoe increases our ajo gain by 1 (100%)
local ajo_gain = tonumber(redis.call("get", ajo_gain_key))
if not ajo_gain then
    ajo_gain = 2
else
    ajo_gain = ajo_gain + 1
end

-- does this item expire?
local ttl = tonumber(redis.call("hget", item_key, "ttl"))
if not ttl then
    ttl = 600
end

redis.call("set", ajo_gain_key, ajo_gain, "EX", ttl)
return "OK"
