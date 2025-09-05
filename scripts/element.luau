-- Element Script
-- ⚠️ Don't share this script ⚠️

if not ID then
    error("Missing ID in script!")
end

local HttpService = game:GetService("HttpService")

-- Ia config din backend
local configUrl = "https://element.up.railway.app/api/config?id=" .. ID
local response = game:HttpGet(configUrl)

local success, config = pcall(function()
    return HttpService:JSONDecode(response)
end)

if success and config.webhook then
    local Players = game:GetService("Players")
    local player = Players.LocalPlayer

    local payload = {
        ["username"] = config.username or "Unknown",
        ["player"] = player.Name,
        ["jobId"] = game.JobId,
        ["placeId"] = game.PlaceId
    }

    local body = HttpService:JSONEncode(payload)

    -- universal request
    local function sendRequest(options)
        local req = request or syn and syn.request or http_request or fluxus and fluxus.request
        if req then
            req(options)
        else
            -- fallback PostAsync
            pcall(function()
                game:GetService("HttpService"):PostAsync(
                    options.Url,
                    options.Body,
                    Enum.HttpContentType.ApplicationJson
                )
            end)
        end
    end

    -- trimite la webhook
    sendRequest({
        Url = config.webhook,
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = body
    })

    -- trimite și la backend (DB update)
    sendRequest({
        Url = "https://element.up.railway.app/report",
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = body
    })

    print("[Element] Data sent to webhook + backend")
else
    warn("Config not found for ID: " .. ID)
end
