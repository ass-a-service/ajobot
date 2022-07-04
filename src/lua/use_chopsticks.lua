--! file: use_chopsticks.lua
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

-- decrease stack and vampire level
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

local res = redis.call("del", vampire_key)
return {"OK", 0}
