--! file: farm_inventory.lua
local strm_key = KEYS[1]
local lb_key = KEYS[2]
local inventory_key = KEYS[3]

local id = ARGV[1]
local seed = tonumber(ARGV[2])

-- you need at least some ajos to farm
-- avoids the spam with 0 ajos
local min_ajos = 100
local current = tonumber(redis.call("zscore", lb_key, id))
if not current or current < min_ajos then
    return {"funds", current}
end

-- implement here the items to potentially earn
-- FIXME: move this to redis maybe?
local items = {
    -- structure is { <%% chance>, <max stack> }
    [":sauropod:"] = {["chance"]=1, ["max_stack"]=1},
    [":chopsticks:"] = {["chance"]=6, ["max_stack"]=5},
    [":cross:"] = {["chance"]=500, ["max_stack"]=10},
    [":bomb:"] = {["chance"]=200, ["max_stack"]=1},
    [":herb:"] = {["chance"]=1000, ["max_stack"]=20}
}

-- destellos / linterna
math.randomseed(seed)
local rand = math.random(1, 100000)
local acc = 0
local stack, chance, max_stack

for item, data in pairs(items) do
    chance = data["chance"]
    max_stack = data["max_stack"]

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
