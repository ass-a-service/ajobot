--! file: craft.lua
local ajo_strm_key = KEYS[1]
local inv_strm_key = KEYS[2]
local lb_key = KEYS[3]
local inventory_key = KEYS[4]
local item_key = KEYS[5]
local craft_key = KEYS[6]

local item = ARGV[1]
local user_id = ARGV[2]
local event_version = ARGV[3]
local guild_id = ARGV[4]

-- ensure we have not reached the max stack yet
local stack = tonumber(redis.call("hget", inventory_key, item))
if not stack then
    stack = 0
end

local max_stack = tonumber(redis.call("hget", item_key, "max_stack"))
if not max_stack then
    return {"unknown", false}
elseif stack >= max_stack then
    return {"stack", false}
end

-- retrieve item data, check if we can pay for everything
local item_data = redis.call("lrange", craft_key, 0, -1)
if not item_data then
    return {"unknown", false}
end

-- assumes that it is not possible to have the same currency multiple times
local size = #item_data
local index = 1
local pay, funds
while index < size do
    currency = vals[index]
    price = vals[index + 1]

    -- all currencies are from inventory apart from garlics
    if currency == ":garlic:" then
        funds = tonumber(redis.call("zscore", lb_key, user_id))
    else
        funds = tonumber(redis.call("hget", inventory_key, currency))
    end

    if not funds or funds < price then
        return {"funds", {currency, price}}
    end
end

-- now that we know we can pay, decrease all currencies
while index < size do
    currency = vals[index]
    price = vals[index + 1]

    if currency == ":garlic:" then
        redis.call("zincrby", lb_key, -price, user_id)
        redis.call(
            "xadd", ajo_strm_key, "*",
            "version", event_version,
            "type", "craft_fee",
            "user_id", user_id,
            "guild_id", guild_id,
            "item", item,
            "amount", -price
        )
    else
        redis.call("hincrby", inventory_key, currency, -price)
        redis.call(
            "xadd", inv_strm_key, "*",
            "version", event_version,
            "type", "craft_fee",
            "user_id", user_id,
            "guild_id", guild_id,
            "item", item,
            "quantity", -price
        )
    end
end

-- finally craft the item
stack = redis.call("hincrby", inventory_key, item, 1)
redis.call(
    "xadd", inv_strm_key, "*",
    "version", event_version,
    "type", "item_crafted",
    "user_id", user_id,
    "guild_id", guild_id,
    "item", item,
    "quantity", 1
)
return {"OK", {item, stack}}
