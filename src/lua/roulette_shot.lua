--! file: roulette_shot.lua
local lb_key = KEYS[1]
local group_key = KEYS[2]

local name = ARGV[1]

-- sanity, does the roulette exist?
local shot = redis.call("get", group_key)
if not shot then
    return {"err", false}
end

-- decrement the group key
local res = redis.call("decrby", group_key)
if res > 0 then
    return {"OK", nil}
end

-- kill the person, remove the roulette
redis.call("zrem", lb_key, name)
redis.call("del", group_key)
return {"shot", nil}
