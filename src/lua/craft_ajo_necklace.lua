--! file: craft_ajo_necklace.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]
local lb_key = KEYS[3]

local item = ARGV[1]
local user_id = ARGV[2]

local max_stack = 1

-- does the user has enough ajos?
local user_ajos = tonumber(redis.call("zscore", lb_key, user_id))
if user_ajos < 50 then
    return {"funds", false}
end

-- do we have another necklace? It cannot stack!
local stack = tonumber(redis.call("hget", inventory_key, item))

if not stack then
    stack = 0
end

if stack >= max_stack then
    return {"stack", false}
end

-- remove 50 ajos from the user
redis.call("zincrby", lb_key, -50, user_id)

-- give the item to the user
stack = redis.call("hincrby", inventory_key, ":reminder_ribbon:", 1)
redis.call("xadd", strm_key, "*", "user_id", user_id, "item", item, "quantity", 1, "type", "item_crafted")
return {"OK", {item, stack}}
