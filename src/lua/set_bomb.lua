--! file: set_bomb.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]
local item_key = KEYS[3]
local cron_key = KEYS[4]

local ttl = tonumber(ARGV[1])
local id = ARGV[2]
local item = ARGV[3]
local event_version = ARGV[4]
local guild_id = ARGV[5]
local seed = tonumber(ARGV[6])

-- sanity check, the bomb only allows timer for a maximum of 8h
if ttl < 0 or ttl > 28800 then
    return {"time", false}
end

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

local time = redis.call("time")
local expected = tonumber(time[1]) + ttl

-- the bomb will set off within a gap of 7min of the set time
math.randomseed(seed)
local actual = math.random(expected - 210, expected + 210)

-- add the bomb to the cron key, its identifier is the user's ID, meaning a user
-- can only set one bomb at a time. An existing bomb will be overwritten
redis.call("zadd", cron_key, actual, id)
return {"OK", expected}
