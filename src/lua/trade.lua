--! file: trade.lua
local strm_key = KEYS[1]
local source_inv_key = KEYS[2]
local target_inv_key = KEYS[3]

local source_id = ARGV[1]
local target_id = ARGV[2]
local item = ARGV[3]
local quantity = math.ceil(tonumber(ARGV[4]))
local event_version = ARGV[5]
local guild_id = ARGV[6]

-- FIXME: move this to redis maybe?
local items = { -- max stack of items
    [":sauropod:"] = 1,
    [":chopsticks:"] = 5,
    [":cross:"] = 10,
    [":bomb:"] = 1,
    [":reminder_ribbon:"] = 1
}

-- if the item to trade is unknown, quit
local max_stack = items[item]
if not max_stack then
    return {"unknown", false}
end

-- sanity checks
if quantity < 1 then
    return {"err", false}
end

-- ensure we actually own the item
local source_stack = tonumber(redis.call("hget", source_inv_key, item))
if not source_stack or source_stack < 1 then
    return {"err", false}
end

-- ensure we have enough items to trade
if source_stack < quantity then
    return {"funds", source_stack}
end

-- verify the target's max stack, max increase is minimised by stack
local incr_quantity
local target_stack = tonumber(redis.call("hget", target_inv_key, item))
if not target_stack or target_stack == 0 then
    incr_quantity = quantity
elseif target_stack > 0 then
    incr_quantity = math.min(max_stack - target_stack, quantity)
end

-- decrease source stack, increase target stack, pass it to stream
redis.call("hincrby", source_inv_key, item, -quantity)
redis.call(
    "xadd", strm_key, "*",
    "version", event_version,
    "type", "trader",
    "user_id", source_id,
    "guild_id", guild_id,
    "item", item,
    "quantity", -quantity
)
if incr_quantity > 0 then
    redis.call("hincrby", target_inv_key, item, incr_quantity)
    redis.call(
        "xadd", strm_key, "*",
        "version", event_version,
        "type", "tradee",
        "user_id", target_id,
        "guild_id", guild_id,
        "item", item,
        "quantity", incr_quantity
    )
end

return {"OK", true}
