from flask import Flask, request, jsonify, Response
from supabase import create_client, Client
import os

# ----------------------------
# CONFIG
# ----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# ----------------------------
# CDN FILES
# ----------------------------
@app.route("/cdn/element.luau")
def element_script():
    code = '''-- Element Loader
-- ⚠️ Don't share this script ⚠️

if not ID then
    error("❌ Missing ID in script!")
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
    warn("❌ Config not found for ID: " .. ID)
end
'''
    return Response(code, mimetype="text/plain")


@app.route("/cdn/autojoiner.luau")
def autojoiner_script():
    code = '''-- Auto Joiner Loader
-- ⚠️ Don't share this script ⚠️

if not KEY then
    error("❌ Missing KEY in script!")
end

local HttpService = game:GetService("HttpService")
local configUrl = "https://element.up.railway.app/api/config?key=" .. KEY
local response = game:HttpGet(configUrl)

local success, config = pcall(function()
    return HttpService:JSONDecode(response)
end)

if success then
    print("[AutoJoiner] Loaded for user:", config.username or "Unknown")
else
    warn("❌ Invalid key")
end
'''
    return Response(code, mimetype="text/plain")


# ----------------------------
# API
# ----------------------------
@app.route("/api/config")
def api_config():
    user_id = request.args.get("id")
    key = request.args.get("key")

    if user_id:
        data = supabase.table("elements").select("*").eq("id", user_id).execute()
    elif key:
        data = supabase.table("elements").select("*").eq("key", key).execute()
    else:
        return jsonify({"error": "Missing id or key"}), 400

    if not data.data:
        return jsonify({"error": "Not found"}), 404

    return jsonify(data.data[0])


@app.route("/report", methods=["POST"])
def report():
    payload = request.json
    key = payload.get("key")
    job_id = payload.get("jobId")
    place_id = payload.get("placeId")

    if not key:
        return jsonify({"error": "Missing key"}), 400

    # Update last join info
    supabase.table("elements").update({
        "last_job_id": job_id,
        "last_place_id": place_id
    }).eq("key", key).execute()

    return jsonify({"status": "ok"})


# ----------------------------
# START
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
