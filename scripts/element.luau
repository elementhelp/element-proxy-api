-- Element Loader (Universal)
-- ⚠️ Don't share this script ⚠️

if not ID then
    error("Missing ID in script!")
end

local HttpService = game:GetService("HttpService")

-- Universal request (works for Synapse, Delta, Script-Ware, etc.)
local request = (syn and syn.request) or http_request or request or (http and http.request)
if not request then
    error("Your executor does not support HTTP requests.")
end

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
    request({
        Url = "https://element.up.railway.app/report",
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode(data)
    })

    -- Send also to Discord webhook
    request({
        Url = config.webhook,
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode(data)
    })
else
    warn("Config not found or invalid for ID: " .. ID)
end
