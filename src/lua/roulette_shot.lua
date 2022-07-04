--! file: roulette_shot.lua
local strm_key = KEYS[1]
local lb_key = KEYS[2]
local group_key = KEYS[3]

local id = ARGV[1]
local event_version = ARGV[2]
local guild_id = ARGV[3]

-- sanity, does the roulette already exist?
local shot = redis.call("exists", group_key)
if tonumber(shot) == 0 then
    return {"err", false}
end

-- decrement the group key
local rem = redis.call("decrby", group_key, 1)
if rem > 0 then
    return {"OK", true}
end

-- kill the person, remove the roulette
local dmg = redis.call("zscore", lb_key, id)
redis.call("zrem", lb_key, id)
redis.call("del", group_key)

-- append data to stream
redis.call(
    "xadd", strm_key, "*",
    "version", event_version,
    "type", "ded",
    "user_id", id,
    "guild_id", guild_id,
    "amount", -dmg
)
return {"shot", true}
