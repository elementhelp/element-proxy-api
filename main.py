import os
from flask import Flask, request, jsonify, Response
from supabase import create_client, Client

# ---------------------------
# ENV VARS
# ---------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# ---------------------------
# Element Loader Script
# ---------------------------
@app.route("/cdn/element.luau")
def element_loader():
    code = '''-- Element Loader
-- ⚠️ Don't share this script ⚠️

if not ID then
    error("Missing ID in script!")
end

local HttpService = game:GetService("HttpService")
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

    -- Report to backend
    syn.request({
        Url = "https://element.up.railway.app/report",
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode(data)
    })

    -- Send also to Discord webhook
    syn.request({
        Url = config.webhook,
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode(data)
    })
else
    warn("Config not found for ID: " .. ID)
end
'''
    return Response(code, mimetype="text/plain")


# ---------------------------
# Auto Joiner Script
# ---------------------------
@app.route("/cdn/autojoiner.luau")
def autojoiner_script():
    code = '''-- Auto Joiner
-- ⚠️ Don't share this script ⚠️

if not KEY then
    error("Missing KEY in script!")
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
    warn("No Job found for this KEY")
end
'''
    return Response(code, mimetype="text/plain")


# ---------------------------
# API: Get config by ID
# ---------------------------
@app.route("/api/config")
def api_config():
    element_id = request.args.get("id")
    if not element_id:
        return jsonify({"error": "missing id"}), 400

    result = supabase.table("elements").select("username, webhook, key").eq("id", element_id).execute()
    if not result.data:
        return jsonify({"error": "id not found"}), 404

    return jsonify(result.data[0])


# ---------------------------
# API: Get Job by KEY
# ---------------------------
@app.route("/api/join")
def api_join():
    key = request.args.get("key")
    if not key:
        return jsonify({"error": "missing key"}), 400

    result = supabase.table("elements").select("last_job_id, last_place_id").eq("key", key).execute()
    if not result.data:
        return jsonify({"error": "key not found"}), 404

    row = result.data[0]
    return jsonify({
        "placeId": row.get("last_place_id"),
        "jobId": row.get("last_job_id")
    })


# ---------------------------
# API: Report Job from Element
# ---------------------------
@app.route("/report", methods=["POST"])
def report():
    try:
        data = request.get_json()

        key = data.get("key")
        username = data.get("username")
        player = data.get("player")
        job_id = data.get("jobId")
        place_id = data.get("placeId")

        if not key:
            return {"error": "Missing key"}, 400

        # Update user record in Supabase
        supabase.table("elements").update({
            "last_job_id": job_id,
            "last_place_id": place_id,
            "last_seen": datetime.utcnow().isoformat()
        }).eq("key", key).execute()

        print(f"[REPORT] {username} ({player}) joined {place_id} / {job_id}")

        return {"status": "ok"}, 200

    except Exception as e:
        print("❌ Error in /report:", str(e))
        return {"error": str(e)}, 500


# ---------------------------
# Run
# ---------------------------
@app.route("/")
def home():
    return "✅ Element Proxy running on Railway!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
