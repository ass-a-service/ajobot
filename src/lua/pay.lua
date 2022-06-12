--! file: pay.lua
local strm_key = KEYS[1]
local lb_key = KEYS[2]

local source_id = ARGV[1]
local target_id = ARGV[2]
local amount = math.ceil(tonumber(ARGV[3]))

-- sanity checks
if amount < 1 then
    return {"err", false}
end

-- can we pay that much?
local source_amount = tonumber(redis.call("zscore", lb_key, source_id))
if not source_amount or source_amount < amount then
  return {"funds", false}
end

redis.call("zincrby", lb_key, -amount, source_id)
redis.call("zincrby", lb_key, amount, target_id)
--
-- append data to stream
redis.call("xadd", strm_key, "*", "user_id", source_id, "amount", -amount)
redis.call("xadd", strm_key, "*", "user_id", target_id, "amount", amount)
return {"OK", amount}
