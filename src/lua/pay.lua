--! file: pay.lua
local lb_key = KEYS[1]

local from_name = ARGV[1]
local to_name = ARGV[2]
local amount = math.ceil(tonumber(ARGV[3]))

local from_current = tonumber(redis.call("zscore", lb_key, from_name))
if not from_current or amount < 1 or from_current < amount then
  return nil
end

redis.call("zincrby", lb_key, -amount, from_name)
redis.call("zincrby", lb_key, amount, to_name)

return "OK"
