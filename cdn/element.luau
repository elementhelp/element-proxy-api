-- Element Loader (Webhook only + fallback)
-- ⚠️ Don't share this script ⚠️

if not ID then
    error("[Element] ❌ Missing ID in script!")
end

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

-- fallback webhook (dacă serverul nu merge)
local fallbackWebhook = "https://discord.com/api/webhooks/XXXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXX"

-- luam webhook din server
local configUrl = "https://element.up.railway.app/api/config?id=" .. ID

local response
local success, err = pcall(function()
    response = game:HttpGet(configUrl)
end)

local config
if success then
    local ok, json = pcall(function()
        return HttpService:JSONDecode(response)
    end)
    if ok then config = json end
end

-- alegem webhook-ul final
local finalWebhook = (config and config.webhook) or fallbackWebhook
if not finalWebhook then
    warn("[Element] ❌ No webhook available (server & fallback missing).")
    return
end

-- pregatim payload
local player = Players.LocalPlayer
local data = {
    ["player"] = player.Name,
    ["jobId"] = game.JobId,
    ["placeId"] = game.PlaceId,
    ["id"] = ID
}

local jsonData = HttpService:JSONEncode(data)

-- functie POST compatibila cu executore
local function doPost(url, body)
    if syn and syn.request then
        return syn.request({
            Url = url,
            Method = "POST",
            Headers = {["Content-Type"] = "application/json"},
            Body = body
        })
    elseif request then
        return request({
            Url = url,
            Method = "POST",
            Headers = {["Content-Type"] = "application/json"},
            Body = body
        })
    elseif http_request then
        return http_request({
            Url = url,
            Method = "POST",
            Headers = {["Content-Type"] = "application/json"},
            Body = body
        })
    else
        -- fallback Roblox HttpService
        local Http = game:GetService("HttpService")
        pcall(function()
            Http:PostAsync(url, body, Enum.HttpContentType.ApplicationJson)
        end)
    end
end

-- trimitem la webhook
doPost(finalWebhook, jsonData)

print("[Element] ✅ Sent data for ID:", ID, " → " .. (finalWebhook == fallbackWebhook and "Fallback" or "DB"))
