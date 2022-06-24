--! file: farm_inventory.lua
local strm_key = KEYS[1]
local lb_key = KEYS[2]
local inventory_key = KEYS[3]

local id = tonumber(ARGV[1])
local seed = tonumber(ARGV[2])

-- you need at least some ajos to farm
-- avoids the spam with 0 ajos
local min_ajos = 100
local current = tonumber(redis.call("zscore", lb_key, id))
if not current or current < min_ajos then
    return {"funds", false}
end

-- implement here the items to potentially earn
local items = {
    -- structure is { <%% chance>, <max stack> }
    [":sauropod:"] = {1, 1},
    [":chopsticks:"] = {6, 5},
    [":cross:"] = {500, 10},
    [":bomb:"] = {200, 1}
}

-- destellos / linterna
math.randomseed(seed)
local rand = math.random(1, 100000)
local acc = 0
local stack

for item, data in pairs(items) do
    chance = data[0]
    max_stack = data[1]

    -- increase our chance of receiving something
    acc = acc + chance

    -- if we're lower than the current chance, we got the item
    if rand <= acc then
        -- ensure we did not reach max stack
        stack = tonumber(redis.call("hget", inventory_key, item))
        if not stack or stack < max_stack then
            stack = redis.call("hincrby", inventory_key, item, 1)
            redis.call("xadd", strm_key, "*", "user_id", id, "item", item, "quantity", 1)
            return {"OK", {item, stack}}
        end

        return {"stack", false}
    end
end

return {"none", false}
