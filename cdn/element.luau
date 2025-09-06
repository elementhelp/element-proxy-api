-- Element Loader
-- Compatibil cu majoritatea executorilor

if not ID then
    error("⚠️ Missing ID in script!")
end

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

-- universal request
local function safeRequest(url, method, body)
    local req = http_request or request or syn.request
    if not req then
        warn("Executorul tau nu suporta http_request")
        return
    end
    local data = {
        Url = url,
        Method = method,
        Headers = { ["Content-Type"] = "application/json" },
        Body = body and HttpService:JSONEncode(body) or nil
    }
    return req(data)
end

-- ia config
local configUrl = "https://element.up.railway.app/api/config?id=" .. ID
local response = safeRequest(configUrl, "GET")
if not response or response.StatusCode ~= 200 then
    warn("Nu am putut lua config pentru ID-ul: " .. tostring(ID))
    return
end

local config = HttpService:JSONDecode(response.Body)

-- functie report
local function reportJob()
    local jobId = game.JobId
    local reportUrl = "https://element.up.railway.app/report"
    safeRequest(reportUrl, "POST", {
        id = ID,
        jobId = jobId
    })
    print("[Element] ✅ Sent data for ID: " .. ID)
end

-- rulează când intră playerul
Players.PlayerAdded:Connect(function(player)
    if player == Players.LocalPlayer then
        reportJob()
    end
end)
