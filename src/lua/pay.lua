--! file: pay.lua
local strm_key = KEYS[1]
local lb_key = KEYS[2]

local source_id = ARGV[1]
local target_id = ARGV[2]
local amount = math.ceil(tonumber(ARGV[3]))
local event_version = ARGV[4]
local guild_id = ARGV[5]

-- sanity checks
if amount < 1 then
    return {"err", false}
end

if source_id == target_id then
    return {"futile", false}
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
redis.call(
    "xadd", strm_key, "*",
    "version", event_version,
    "type", "payer",
    "user_id", source_id,
    "guild_id", guild_id,
    "amount", -amount
)
redis.call(
    "xadd", strm_key, "*",
    "version", event_version,
    "type", "payee",
    "user_id", target_id,
    "guild_id", guild_id,
    "amount", amount
)
return {"OK", amount}
