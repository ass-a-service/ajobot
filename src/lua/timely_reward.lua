--! file: timely_reward.lua
local strm_key = KEYS[1]
local lb_key = KEYS[2]
local timely_key = KEYS[3]

local id = ARGV[1]
local reward = math.ceil(tonumber(ARGV[2]))
local expire = tonumber(ARGV[3])
local event_version = ARGV[4]
local guild_id = ARGV[5]

-- is this reward available?
local ttl = tonumber(redis.call("ttl", timely_key))
if ttl > 0 then
    return {"ttl", ttl}
end

redis.call("zincrby", lb_key, reward, id)
redis.call("set", timely_key, 1, "ex", expire)

-- append data to stream
redis.call(
    "xadd", strm_key, "*",
    "version", event_version,
    "type", "timely_reward",
    "user_id", id,
    "guild_id", guild_id,
    "amount", reward
)
return {"OK", reward}
