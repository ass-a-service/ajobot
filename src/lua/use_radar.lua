--! file: use_radar.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]
local cron_key = KEYS[3]

local id = ARGV[1]
local item = ARGV[2]
local event_version = ARGV[3]
local guild_id = ARGV[4]

-- ensure we actually own the item
local stack = tonumber(redis.call("hget", inventory_key, item))
if not stack or stack < 1 then
    return {"err", false}
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

-- the radar shows the next five bomb to detonate, if any
local bombs = redis.call(
    "zrange",
    cron_key,
    "0",
    "+inf",
    "byscore",
    "limit",
    0,
    5,
    "withscores"
)
return {"OK", bombs}
