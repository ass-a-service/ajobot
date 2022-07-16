--! file: roulette.lua
local group_key = KEYS[1]

local expire = tonumber(ARGV[1])

redis.replicate_commands()

-- sanity, does the roulette already exist?
local shot = redis.call("exists", group_key)
if tonumber(shot) ~= 0 then
    return {"err", false}
end

-- group expires in 10min, assign the shot number to that group
redis.call("set", group_key, math.random(1, 6), "ex", expire)
return {"OK", true}
