-- ✅ Element Loader fix pentru executori cu http_request
if not ID then
    error("⚠️ Missing ID in script!")
end

local HttpService = game:GetService("HttpService")

-- Funcția de request (bazată doar pe http_request)
local function send_request(options)
    if http_request then
        return http_request(options)
    elseif request then
        return request(options)
    else
        error("❌ Executorul tău nu suportă http_request sau request!")
    end
end

-- Ia config-ul din backend
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

    -- Trimite datele la backend
    send_request({
        Url = "https://element.up.railway.app/report",
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode(data)
    })

    -- Trimite și la webhook
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
