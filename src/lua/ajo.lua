--! file: vampire.lua
local strm_key = KEYS[1]
local lb_key = KEYS[2]
local ajo_gain_key = KEYS[3]
local vampire_key = KEYS[4]
local name_key = KEYS[5]
local bomb_key = KEYS[6]

local id = ARGV[1]
local called_name = ARGV[2]
local event_version = ARGV[3]
local guild_id = ARGV[4]

-- avoid infinite ajo spam, if the vampire is that high, we quit
local level = tonumber(redis.call("get", vampire_key))
if level and level > 69 then
    return {"err", false}
end

-- check for a potential bomb
local bomb = redis.call("get", bomb_key)
if bomb then
    redis.call("del", bomb_key)

    -- if the user has nothing, nothing happens
    local current = tonumber(redis.call("zscore", lb_key, id))
    if not current or current == 0 then
        return {"bomb", {bomb, 0}}
    end

    -- set off the bomb, apply damage
    local pct_dmg = 18
    local dmg = math.floor(current * (pct_dmg / 100))
    redis.call("zincrby", lb_key, -dmg, id)
    redis.call(
        "xadd", strm_key, "*",
        "version", event_version,
        "type", "bomb",
        "user_id", id,
        "guild_id", guild_id,
        "amount", -dmg
    )
    return {"bomb", {bomb, dmg}}
end

-- check our effects for ajo efficiency
local ajo_gain = tonumber(redis.call("get", ajo_gain_key))
if not ajo_gain then
    ajo_gain = 1
end

-- add the ajos and update the stream
if ajo_gain ~= 0 then
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
end

return {"OK", 0}
