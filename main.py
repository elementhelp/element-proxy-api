import os
import requests
from flask import Flask, request, jsonify
from supabase import create_client, Client

# 🔑 Variabile de mediu (setate pe Railway)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# 📦 Conectare Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🚀 Flask API
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Element API is running on Railway!"

@app.route("/report", methods=["POST"])
def report():
    """
    Endpoint apelat de scriptul din Roblox
    Trimite: { "user_id": "...", "username": "...", "job_id": "..." }
    """
    data = request.json
    user_id = data.get("user_id")
    username = data.get("username")
    job_id = data.get("job_id")

    if not user_id or not username or not job_id:
        return jsonify({"error": "Missing fields"}), 400

    # 📦 Salvăm în Supabase
    supabase.table("reports").insert({
        "user_id": user_id,
        "username": username,
        "job_id": job_id
    }).execute()

    # 🔔 Trimitem și pe webhook
    if DISCORD_WEBHOOK:
        requests.post(DISCORD_WEBHOOK, json={
            "embeds": [{
                "title": "📡 Element Report",
                "fields": [
                    {"name": "User ID", "value": user_id, "inline": True},
                    {"name": "Username", "value": username, "inline": True},
                    {"name": "Job ID", "value": job_id, "inline": False}
                ],
                "color": 0x2ecc71
            }]
        })

    return jsonify({"status": "success", "message": "Report saved"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
