--! file: vampire.lua
local strm_key = KEYS[1]
local lb_key = KEYS[2]
local ajo_gain_key = KEYS[3]
local vampire_key = KEYS[4]
local name_key = KEYS[5]

local id = ARGV[1]
local called_name = ARGV[2]
local event_version = ARGV[3]
local guild_id = ARGV[4]

-- avoid infinite ajo spam, if the vampire is that high, no ajos
local level = tonumber(redis.call("get", vampire_key))
if level and level > 69 then
    return {"err", false}
end

-- check our effects for ajo efficiency
local ajo_gain = redis.call("get", ajo_gain_key)
if not ajo_gain then
    ajo_gain = 1
end

-- add the ajos and update the stream
redis.call("zincrby", lb_key, ajo_gain, id)
redis.call(
    "xadd", strm_key, "*",
    "version", event_version,
    "type", "farm",
    "user_id", id,
    "guild_id", guild_id,
    "amount", ajo_gain
)

-- update our username if it has changed
local current_name = redis.call("get", name_key)
if called_name ~= current_name then
    redis.call("set", name_key, called_name)
end

return {"OK", ajo_gain}
