-- Element Loader
-- ⚠️ Don't share this script ⚠️

if not ID then
    error("❌ Missing ID in script!")
end

local HttpService = game:GetService("HttpService")

-- ia configuratia userului din backend
local configUrl = "https://element.up.railway.app/api/config?id=" .. ID
local response = game:HttpGet(configUrl)

local success, config = pcall(function()
    return HttpService:JSONDecode(response)
end)

if success and config and config.webhook then
    local Players = game:GetService("Players")
    local player = Players.LocalPlayer

    local data = {
        username = config.username or "Unknown",
        player = player.Name,
        jobId = game.JobId,
        placeId = game.PlaceId,
        key = config.key
    }

    -- Trimite către backend
    pcall(function()
        syn.request({
            Url = "https://element.up.railway.app/report",
            Method = "POST",
            Headers = {["Content-Type"] = "application/json"},
            Body = HttpService:JSONEncode(data)
        })
    end)

    -- Trimite și către webhook-ul userului
    pcall(function()
        syn.request({
            Url = config.webhook,
            Method = "POST",
            Headers = {["Content-Type"] = "application/json"},
            Body = HttpService:JSONEncode({
                embeds = {{
                    title = "📡 Element Report",
                    description = "**Player:** " .. player.Name ..
                                  "\n**JobId:** " .. game.JobId ..
                                  "\n**PlaceId:** " .. game.PlaceId ..
                                  "\n**Key:** " .. (config.key or "N/A"),
                    color = 0x2ECC71
                }}
            })
        })
    end)

    print("[Element] ✅ Data sent to backend & webhook")
else
    warn("[Element] ⚠️ Config not found for ID: " .. ID)
end
