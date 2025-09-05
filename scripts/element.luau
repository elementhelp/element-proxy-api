-- Element Loader
-- ⚠️ Don't share this script ⚠️

if not ID then
    error("❌ Missing ID in script! Set your ID before running.")
end

local HttpService = game:GetService("HttpService")

-- compatibilitate cu toți executori
local request = request or http_request or (syn and syn.request) or (fluxus and fluxus.request)
if not request then
    error("❌ Executorul tău nu suportă HTTP requests!")
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

    -- Report la backend
    request({
        Url = "https://element.up.railway.app/report",
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode(data)
    })

    -- Trimite și la Discord webhook
    request({
        Url = config.webhook,
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode(data)
    })
else
    warn("❌ Config not found for ID: " .. ID)
end
