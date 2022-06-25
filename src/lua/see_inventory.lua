--! file: see_inventory.lua
local strm_key = KEYS[1]
local lb_key = KEYS[2]
local inventory_key = KEYS[3]

local id = ARGV[1]

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
redis.call("xadd", strm_key, "*", "user_id", id, "amount", -fee, "type", "inventory_fee")
return {"OK", items}
