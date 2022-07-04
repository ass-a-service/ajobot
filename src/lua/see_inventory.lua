--! file: see_inventory.lua
local strm_key = KEYS[1]
local lb_key = KEYS[2]
local inventory_key = KEYS[3]

local id = ARGV[1]
local event_version = ARGV[2]
local guild_id = ARGV[3]

-- can we pay to see the inventory?
local fee = 10
local current = tonumber(redis.call("zscore", lb_key, id))
if not current or current < fee then
    return {"funds", fee}
end

-- retrieve the inentory values
local items = redis.call("hgetall", inventory_key)

-- pay the fee and append to stream
redis.call("zincrby", lb_key, -fee, id)
redis.call(
    "xadd", strm_key, "*",
    "version", event_version,
    "type", "inventory_fee",
    "user_id", id,
    "guild_id", guild_id,
    "amount", -fee
)
return {"OK", items}
