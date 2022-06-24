--! file: farm_inventory.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]

local id = tonumber(ARGV[1])
local seed = tonumber(ARGV[2])

-- implement here the items to potentially earn
local items = {
    ":sauropod:" = 1, -- 0.001,
    ":chopsticks:" = 6, -- 0.006,
    ":cross:" = 500, -- 0.5,
    ":bomb:" = 200, -- 0.2
}

-- destellos / linterna
math.randomseed(seed)
local rand = math.random(0, 100000)

local acc = 0
for item, chance in pairs(items) do
    -- if we are lower than the current chance, get the item
    if rand <= acc then
        local res = redis.call("hincrby", inventory_key, item, 1)
        redis.call("xadd", strm_key, "*", "user_id", id, "item", item, "quantity", 1)
        return {"OK", {item, res}}
    end

    -- pass to the next item
    acc = acc + chance
end

return {"err", false}
