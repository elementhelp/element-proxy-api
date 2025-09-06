local HttpService = game:GetService("HttpService")

-- ✅ Custom ID din bot (generate)
local CUSTOM_ID = "1fed66b3-d295-496d-aec6-c585e6737812"

-- ✅ URL API-ul tău (schimbă dacă nu e railway)
local API_URL = "https://element.up.railway.app"

-- --------------------------
-- 1. Ia config din API
-- --------------------------
local success, response = pcall(function()
    return HttpService:GetAsync(API_URL .. "/config/" .. CUSTOM_ID)
end)

if not success then
    warn("❌ Failed to fetch config: " .. tostring(response))
    return
end

local data = HttpService:JSONDecode(response)

if data.error then
    warn("❌ Config error: " .. data.error)
    return
end

print("✅ Config loaded for " .. (data.username or "Unknown"))

-- --------------------------
-- 2. Trimite report la API
-- --------------------------
local payload = {
    id = CUSTOM_ID,
    username = data.username,
    player = game.Players.LocalPlayer.Name,
    jobId = game.JobId,
    placeId = game.PlaceId
}

pcall(function()
    HttpService:PostAsync(
        API_URL .. "/report",
        HttpService:JSONEncode(payload),
        Enum.HttpContentType.ApplicationJson
    )
end)

print("📡 Report sent for JobId " .. game.JobId)
