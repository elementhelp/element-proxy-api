from flask import Flask, request, jsonify
from supabase import create_client, Client
import os
import requests

# ---------------------------
# CONFIG
# ---------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# ---------------------------
# ROUTE: Home
# ---------------------------
@app.route("/")
def home():
    return "✅ Element Proxy API Running!"

# ---------------------------
# ROUTE: Get Config for Element Script
# ---------------------------
@app.route("/api/config/<custom_id>")
def get_config(custom_id: str):
    result = supabase.table("users").select("username, webhook_url, key").eq("custom_id", custom_id).execute()

    if not result.data:
        return jsonify({"error": f"No config found for ID {custom_id}"}), 404

    return jsonify({
        "id": custom_id,
        "username": result.data[0].get("username"),
        "webhook_url": result.data[0].get("webhook_url"),
        "key": result.data[0].get("key")
    })

# ---------------------------
# ROUTE: Report from Roblox
# ---------------------------
@app.route("/report", methods=["POST"])
def report():
    try:
        data = request.get_json()

        if not data or "id" not in data:
            return jsonify({"error": "Missing ID in payload"}), 400

        element_id = data["id"]
        username = data.get("username")
        player = data.get("player")
        job_id = data.get("jobId")
        place_id = data.get("placeId")

        # Update in database
        supabase.table("users").update({
            "last_job_id": job_id,
            "last_place_id": place_id,
            "last_player": player
        }).eq("custom_id", element_id).execute()

        # Fetch webhook
        result = supabase.table("users").select("webhook_url").eq("custom_id", element_id).execute()
        webhook = result.data[0]["webhook_url"] if result.data and result.data[0].get("webhook_url") else None

        # Send to webhook if exists
        if webhook:
            payload = {
                "content": f"🎮 **Element Report**\n"
                           f"👤 Player: `{player}`\n"
                           f"🆔 JobId: `{job_id}`\n"
                           f"📍 PlaceId: `{place_id}`\n"
                           f"💾 Username: `{username or 'Unknown'}`"
            }
            try:
                requests.post(webhook, json=payload, timeout=5)
            except Exception as e:
                print(f"❌ Failed to send to webhook: {e}")

        return jsonify({"status": "ok", "message": "Report processed"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
