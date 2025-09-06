-- Element Script (Template)
local ID = "{ID}"
local WEBHOOK = "{WEBHOOK}"

game.Players.PlayerAdded:Connect(function(player)
    local data = {
        username = player.Name,
        jobId = game.JobId,
        placeId = game.PlaceId
    }
    syn.request({
        Url = WEBHOOK,
        Method = "POST",
        Body = game:GetService("HttpService"):JSONEncode(data),
        Headers = {["Content-Type"] = "application/json"}
    })
end)
