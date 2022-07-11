--! file: vampire.lua
local strm_key = KEYS[1]
local lb_key = KEYS[2]
local vampire_key = KEYS[3]
local curse_key = KEYS[4]
local inventory_key = KEYS[5]

local id = ARGV[1]
local event_version = ARGV[2]
local guild_id = ARGV[3]
local seed = tonumber(ARGV[4])

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

-- if the user is cursed, the appear chance is increased
local curse = tonumber(redis.call("get", curse_key))
if curse and curse > 0 then
    appear_chance = appear_chance + curse
end

-- quit if the vampire does not appear
math.randomseed(seed)
local rand = math.random(0, 99)
if appear_chance < rand then
    return {"OK", false}
end

-- determine damage of the vampire and its ttl
local ttl_per_level = 600
local current = tonumber(redis.call("zscore", lb_key, id))
local ttl = math.min(ttl_per_level * level, 7200)

-- if we don't have any ajos, refresh the vampire's current TTL but do not damage
-- this is here to mess with spammers
if not current or current < 1 then
    redis.call("expire", vampire_key, ttl)
    return {"OK", false}
end

-- calculate damage
local dmg, min, max, pct_dmg, op_result

-- is it protected with a necklace?
local has_necklace = redis.call("hget", inventory_key, ":reminder_ribbon:")
if has_necklace and tonumber(has_necklace) >= 1 then
    dmg = 0
    -- Remove the necklace by 1
    redis.call("hincrby", inventory_key, ":reminder_ribbon:", -1)
    op_result = "NECKLACE"
else
    min = math.min(level * 1.2, 30)
    max = math.min(40, level * 2)
    pct_dmg = math.random(min, max)
    dmg = math.ceil(current * (pct_dmg / 100))
    op_result = "OK"
end

-- increase the vampire's level, refresh his ttl
redis.call("set", vampire_key, level + 1, "EX", ttl)

-- apply damage, add to stream
redis.call("zincrby", lb_key, -dmg, id)
redis.call(
    "xadd", strm_key, "*",
    "version", event_version,
    "type", "vampire",
    "user_id", id,
    "guild_id", guild_id,
    "amount", -dmg
)
return {op_result, {level, dmg}}
