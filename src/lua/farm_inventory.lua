--! file: farm_inventory.lua
local strm_key = KEYS[1]
local items_key = KEYS[2]
local lb_key = KEYS[3]
local inventory_key = KEYS[4]

local id = ARGV[1]
local event_version = ARGV[2]
local guild_id = ARGV[3]
local event_id = ARGV[4] -- the redis event_id trigger

redis.replicate_commands()

-- you need at least some ajos to farm
-- avoids the spam with 0 ajos
local min_ajos = 100
local current = tonumber(redis.call("zscore", lb_key, id))
if not current or current < min_ajos then
    return {"funds", current}
end

-- retrieve redis drop rate and maxstack data
local rand = math.random(1, 100000)
local acc = 0
local item, drop_rate, max_stack

-- retrieve our drop rate from redis
local vals = redis.call("lrange", items_key, 0, -1)
local size = #vals
local index = 1
while index < size do
    item = vals[index]
    drop_rate = tonumber(vals[index + 1])
    max_stack = tonumber(vals[index + 2])
    index = index + 3

    -- increase our chance of receiving something
    acc = acc + drop_rate

    -- if we're lower than the current chance, we got the item
    if rand <= acc then
        -- ensure we did not reach max stack
        local stack = tonumber(redis.call("hget", inventory_key, item))
        if not stack or stack < max_stack then
            stack = redis.call("hincrby", inventory_key, item, 1)
            redis.call(
                "xadd", strm_key, "*",
                "version", event_version,
                "type", "item_earned",
                "user_id", id,
                "guild_id", guild_id,
                "event_id", event_id,
                "item", item,
                "quantity", 1
            )
            return {"OK", {item, stack}}
        end

        return {"stack", false}
    end
end

return {"none", false}
