-- Element Loader
-- ⚠️ Don't share this script ⚠️

if not ID then
    error("❌ Missing ID in script! Please set ID=\"...\" at the top.")
end

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local player = Players.LocalPlayer

-- URL către API-ul tău (proxy/railway)
local configUrl = "https://element.up.railway.app/api/config?id=" .. ID

-- Ia config din backend
local success, response = pcall(function()
    return game:HttpGet(configUrl)
end)

if not success then
    warn("❌ Failed to fetch config from API: " .. tostring(response))
    return
end

local ok, config = pcall(function()
    return HttpService:JSONDecode(response)
end)

if not ok or not config then
    warn("❌ Invalid config for ID: " .. ID)
    return
end

-- Construim datele ce se trimit
local data = {
    ["username"] = config.username or "Unknown",
    ["player"] = player.Name,
    ["jobId"] = game.JobId,
    ["placeId"] = game.PlaceId,
    ["id"] = ID
}

-- Trimite raport la backend
pcall(function()
    syn.request({
        Url = "https://element.up.railway.app/report",
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode(data)
    })
end)

-- Trimite și la webhook-ul din DB
if config.webhook_url then
    pcall(function()
        syn.request({
            Url = config.webhook_url,
            Method = "POST",
            Headers = {["Content-Type"] = "application/json"},
            Body = HttpService:JSONEncode(data)
        })
    end)
else
    warn("⚠️ No webhook set for ID: " .. ID)
end
