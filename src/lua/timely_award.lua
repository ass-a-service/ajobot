--! file: timely_award.lua
local lb_key = KEYS[1]
local timely_key = KEYS[2]

local name = ARGV[1]
local award = math.ceil(tonumber(ARGV[2]))
local expire = tonumber(ARGV[3])

local ttl = tonumber(redis.call("ttl", timely_key))
if ttl > 0 then
  return ttl
end

redis.call("zincrby", lb_key, award, name)
redis.call("set", timely_key, 1, "ex", expire)

return "OK"
