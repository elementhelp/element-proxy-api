-- Element Loader
-- ⚠️ Don't share this script ⚠️

if not ID then
    error("[Element] ❌ Missing ID in script!")
end

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

-- URL backend unde se ia configuratia
local configUrl = "https://element.up.railway.app/api/config?id=" .. ID

-- luam config din backend
local response
local success, err = pcall(function()
    response = game:HttpGet(configUrl)
end)

if not success then
    warn("[Element] ❌ Failed to fetch config: " .. tostring(err))
    return
end

local config
success, err = pcall(function()
    config = HttpService:JSONDecode(response)
end)

if not success or not config then
    warn("[Element] ❌ Failed to decode config: " .. tostring(err))
    return
end

-- verificam daca are webhook
if not config.webhook then
    warn("[Element] ⚠️ No webhook set for ID: " .. ID)
    return
end

-- pregatim payload
local player = Players.LocalPlayer
local data = {
    ["username"] = config.username or "Unknown",
    ["player"] = player.Name,
    ["jobId"] = game.JobId,
    ["placeId"] = game.PlaceId,
    ["key"] = config.key or "N/A"
}

local jsonData = HttpService:JSONEncode(data)

-- functie de POST cross executor
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
        if Http and Http.PostAsync then
            pcall(function()
                Http:PostAsync(url, body, Enum.HttpContentType.ApplicationJson)
            end)
        else
            warn("[Element] ❌ No HTTP method available in executor!")
        end
    end
end

-- raportam la backend
doPost("https://element.up.railway.app/report", jsonData)

-- raportam si la webhook-ul userului
doPost(config.webhook, jsonData)

print("[Element] ✅ Data sent for ID:", ID)
