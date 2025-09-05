import os
from flask import Flask, request, Response, jsonify
from supabase import create_client, Client

# Flask
app = Flask(__name__)

# Supabase connection
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------------------------
# ELEMENT SCRIPT
# ---------------------------
@app.route("/element.lua")
def element():
    user_id = request.args.get("id", "UNKNOWN_ID")

    # Obținem datele utilizatorului din DB
    result = supabase.table("elements").select("webhook, username").eq("user_id", user_id).execute()
    data = result.data[0] if result.data else {}

    webhook = data.get("webhook", "NOT_SET")
    username = data.get("username", "Guest")

    script = f'''
-- Element Script
local HttpService = game:GetService("HttpService")
local url = "{webhook}"

local function sendData()
    local data = {{
        username = "{username}",
        jobId = game.JobId,
        placeId = game.PlaceId
    }}

    local json = HttpService:JSONEncode(data)
    request = http_request or request or HttpPost or syn.request

    if request then
        request({{
            Url = url,
            Method = "POST",
            Headers = {{["Content-Type"] = "application/json"}},
            Body = json
        }})
    end
end

sendData()
    '''
    return Response(script, mimetype="text/plain")


# ---------------------------
# AUTOJOINER SCRIPT
# ---------------------------
@app.route("/autojoiner.lua")
def autojoiner():
    user_id = request.args.get("id", "UNKNOWN_ID")

    script = f'''
-- Autojoiner Script
local HttpService = game:GetService("HttpService")
local TeleportService = game:GetService("TeleportService")
local Players = game:GetService("Players")

local ELEMENT_ID = "{user_id}"
local API_URL = "https://{request.host}/get_job?id=" .. ELEMENT_ID

local function getJobData()
    local success, response = pcall(function()
        return HttpService:GetAsync(API_URL)
    end)

    if success then
        local data = HttpService:JSONDecode(response)
        if data and data.job_id and data.place_id then
            return data
        else
            warn("❌ Nu am primit job_id sau place_id.")
        end
    else
        warn("❌ Eroare la conectarea la API: " .. tostring(response))
    end
    return nil
end

local function joinJob()
    local jobData = getJobData()
    if jobData then
        print("✅ Gasit job_id: " .. jobData.job_id .. " | place_id: " .. jobData.place_id)
        TeleportService:TeleportToPlaceInstance(jobData.place_id, jobData.job_id, Players.LocalPlayer)
    else
        warn("⚠️ Niciun job disponibil pentru acest ID.")
    end
end

Players.LocalPlayer.OnTeleport:Connect(function(State)
    if State == Enum.TeleportState.Failed then
        warn("❌ Teleport failed, retrying...")
        task.wait(5)
        joinJob()
    end
end)

joinJob()
    '''
    return Response(script, mimetype="text/plain")


# ---------------------------
# API pentru Autojoiner (returnează job_id și place_id din DB)
# ---------------------------
@app.route("/get_job")
def get_job():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"error": "missing id"}), 400

    result = supabase.table("reports").select("job_id, place_id").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
    data = result.data[0] if result.data else {}

    return jsonify(data)


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
