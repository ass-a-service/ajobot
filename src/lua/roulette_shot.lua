--! file: roulette_shot.lua
local lb_key = KEYS[1]
local group_key = KEYS[2]

local name = ARGV[1]

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
redis.call("zrem", lb_key, name)
redis.call("del", group_key)
return {"shot", true}
