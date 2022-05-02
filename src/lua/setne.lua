--! setne.lua
local name_key = KEYS[1]

local called_name = ARGV[1]
local current_name = redis.call("get", name_key)
if called_name ~= current_name then
    redis.call("set", name_key, called_name)
end

return "OK"
