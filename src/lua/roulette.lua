--! file: roulette.lua
local strm_key = KEYS[1]
local group_key = KEYS[2]

local seed = tonumber(ARGV[1])
local expire = tonumber(ARGV[2])

-- sanity, does the roulette already exist?
local shot = redis.call("exists", group_key)
if tonumber(shot) ~= 0 then
    return {"err", false}
end

-- define which of the 6 shot will ruleta
math.randomseed(seed)

-- group expires in 10min, assign the shot number to that group
redis.call("set", group_key, math.random(1, 6), "ex", expire)
return {"OK", true}
