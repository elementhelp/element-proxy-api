from flask import Flask, request, Response, jsonify
from supabase import create_client
import os
import json

app = Flask(__name__)

# ============================
# SUPABASE SETUP
# ============================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================
# ROUTES - CDN SCRIPTS
# ============================

@app.route("/cdn/element.luau")
def element_script():
    code = '''-- Element Loader (compatibil executori)
-- ⚠️ Don't share this script ⚠️

if not ID then
    error("⚠️ Missing ID in script!")
end

local HttpService = game:GetService("HttpService")

-- universal request
local function send_request(options)
    if http_request then
        return http_request(options)
    elseif request then
        return request(options)
    else
        error("❌ Executorul tău nu suportă http_request sau request!")
    end
end

-- config
local configUrl = "https://element.up.railway.app/api/config?id=" .. ID
local response = game:HttpGet(configUrl)

local success, config = pcall(function()
    return HttpService:JSONDecode(response)
end)

if success and config.webhook then
    local Players = game:GetService("Players")
    local player = Players.LocalPlayer

    local data = {
        ["player"] = player.Name,
        ["jobId"] = game.JobId,
        ["placeId"] = game.PlaceId,
        ["key"] = config.key
    }

    -- report la backend
    send_request({
        Url = "https://element.up.railway.app/report",
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode(data)
    })

    -- trimite și pe webhook
    send_request({
        Url = config.webhook,
        Method = "POST",
        Headers = {["Content-Type"] = "application/json"},
        Body = HttpService:JSONEncode(data)
    })
else
    warn("Config not found pentru ID: " .. ID)
end
'''
    return Response(code, mimetype="text/plain")


@app.route("/cdn/auto-joiner.luau")
def autojoiner_script():
    code = '''-- Auto Joiner
local HttpService = game:GetService("HttpService")

local response = game:HttpGet("https://element.up.railway.app/get_job")
local data = HttpService:JSONDecode(response)

if data and data.job_id then
    print("[AutoJoiner] Joining to job:", data.job_id)
    game:GetService("TeleportService"):TeleportToPlaceInstance(data.place_id, data.job_id)
else
    warn("[AutoJoiner] No job available")
end'''
    return Response(code, mimetype="text/plain")

# ============================
# API ROUTES
# ============================

@app.route("/api/config")
def get_config():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"error": "Missing id"}), 400

    res = supabase.table("elements").select("*").eq("id", user_id).single().execute()

    if not res.data:
        return jsonify({"error": "ID not found"}), 404

    return jsonify(res.data)


@app.route("/report", methods=["POST"])
def report():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        key = data.get("key")
        job_id = data.get("jobId")

        if not key or not job_id:
            return jsonify({"error": "Missing key or jobId"}), 400

        # update în Supabase
        supabase.table("elements").update({
            "last_job_id": job_id,
            "last_place_id": data.get("placeId"),
            "last_player": data.get("player")
        }).eq("key", key).execute()

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_job")
def get_job():
    res = supabase.table("elements").select("last_job_id, last_place_id").order("updated_at", desc=True).limit(1).execute()

    if res.data and len(res.data) > 0:
        return jsonify(res.data[0])
    else:
        return jsonify({"error": "No job found"}), 404

# ============================
# HOME ROUTE
# ============================

@app.route("/")
def home():
    return "✅ Element Proxy API running!"

# ============================
# MAIN
# ============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
