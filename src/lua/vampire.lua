--! file: vampire.lua
local strm_key = KEYS[1]
local lb_key = KEYS[2]
local vampire_key = KEYS[3]

local id = ARGV[1]
local seed = tonumber(ARGV[2])

local ttl_per_level = 600

-- grab the vampire level that would appear (not current)
local level = tonumber(redis.call("get", vampire_key))
if not level then
    level = 1
end

-- calculate appear chance
local appear_chance
if level == 1 then
    appear_chance = 1
else
    appear_chance = math.log10(level) * 20
end

-- quit if the vampire does not appear
math.randomseed(seed)
local rand = math.random(0, 99)
if appear_chance < rand then
    return {"OK", false}
end

-- determine damage of the vampire and its ttl
local current = tonumber(redis.call("zscore", lb_key, id))
local ttl = math.min(ttl_per_level * level, 7200)

-- if we don't have any ajos, refresh the vampire's current TTL but do not damage
-- this is here to mess with spammers
if not current or current < 1 then
    redis.call("expire", vampire_key, ttl)
    return {"OK", false}
end

-- calculate damage
local min = math.min(level * 1.2, 30)
local max = math.max(40, level * 2)
local pct_dmg = math.random(min, max)
local dmg = math.ceil(current * (pct_dmg / 100))

-- increase the vampire's level, refresh his ttl
redis.call("set", vampire_key, level + 1, "EX", ttl)

-- apply damage, add to stream
redis.call("xadd", strm_key, "*", "user_id", id, "amount", -dmg)
redis.call("zincrby", lb_key, -dmg, id)
return {"OK", {level, dmg}}
