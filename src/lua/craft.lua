--! file: craft.lua
local strm_key = KEYS[1]
local inventory_key = KEYS[2]
local lb_key = KEYS[3]

local item = ARGV[1]
local user_id = ARGV[2]
local event_version = ARGV[3]
local guild_id = ARGV[4]

-- implement here the items to potentially earn
-- FIXME: move this to redis maybe?
local items = {
    -- structure is { <%% chance>, <max stack> }
    [":cross:"] = {["max_stack"]=10, ["currency"]={[":herb:"]=4}},
    [":reminder_ribbon:"] = {["max_stack"]=1, ["currency"]="ajos", ["price"]=50}
}

local max_stack = items[item]["max_stack"]

-- do we have another cross? It cannot stack!
local stack = tonumber(redis.call("hget", inventory_key, item))

if not stack then
    stack = 0
end

if stack >= max_stack then
    return {"stack", false}
end

-- does the user has enough?
if items[item]["currency"] == "ajos" then
    -- if it's paid with ajos: do we have enough ajos?
    local user_ajos = tonumber(redis.call("zscore", lb_key, user_id))
    if user_ajos < items[item]["price"] then
        return {"funds", false}
    end
else
    -- if it's paid with items: do we have enough items?
    local inventory_funds
    for item_loop, amount in pairs(items[item]["currency"]) do
        inventory_funds = tonumber(redis.call("hget", inventory_key, item_loop))
        if inventory_funds < amount then
            return {"funds", false}
        end
    end
end

-- remove currency from the user
if items[item]["currency"] == "ajos" then
    -- if ajos: remove ajos
    redis.call("zincrby", lb_key, -items[item]["price"], user_id)
else
    -- if inventory: remove inventory
    for item_loop, amount in pairs(items[item]["currency"]) do
        --[":cross:"] = {["max_stack"]=10, ["currency"]={[":herb:"]=4}},
        redis.call("hincrby", inventory_key, item_loop, -amount)
    end
end

-- give the item to the user
stack = redis.call("hincrby", inventory_key, item, 1)
redis.call(
    "xadd", strm_key, "*",
    "version", event_version,
    "type", "item_crafted",
    "user_id", user_id,
    "guild_id", guild_id,
    "item", item,
    "quantity", 1
)
return {"OK", {item, stack}}
