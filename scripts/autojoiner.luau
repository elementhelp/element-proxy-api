-- Auto Joiner
-- ⚠️ Don't share this script ⚠️

if not KEY then
    error("❌ Missing KEY in script! Set your KEY before running.")
end

local HttpService = game:GetService("HttpService")
local apiUrl = "https://element.up.railway.app/api/join?key=" .. KEY
local response = game:HttpGet(apiUrl)

local success, data = pcall(function()
    return HttpService:JSONDecode(response)
end)

if success and data.jobId then
    game:GetService("TeleportService"):TeleportToPlaceInstance(data.placeId, data.jobId)
else
    warn("❌ No Job found for this KEY")
end
