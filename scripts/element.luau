-- ✅ Element Loader (compatibil cu mai mulți executori)
-- ⚠️ Don't share this script ⚠️

if not ID then
    error("⚠️ Missing ID in script!")
end

local HttpService = game:GetService("HttpService")

-- Universal request function
local function send_request(options)
    if http_request then
        return http_request(options)
    elseif request then
        return request(options)
    else
        error("❌ Executorul tău nu suportă http_request sau request!")
    end
end

-- Get user config
local configUrl = "https://element.up.railway.app/api/config?id=" .. ID
local response = game:HttpGet(configUrl)

local success, config = pcall(function()
    return HttpService:JSONDecode(response)
end)

if success and config.webhook then
    local Players = game:GetService("Players")
    local player = Players.LocalPlayer
    local data = {
        ["username"] = config.username or "Unknown",
        ["player"] = player.Name,
        ["jobId"] = game.JobId,
        ["placeId"] = game.PlaceId,
        ["key"] = config.key
    }

    -- Report to backend
    send_request({
        Url = "https://element.up.railway.app/report",
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode(data)
    })

    -- Send also to Discord webhook
    send_request({
        Url = config.webhook,
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode(data)
    })

    print("[Element] ✅ Data sent successfully")
else
    warn("⚠️ Config not found for ID: " .. ID)
end
