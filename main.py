from flask import Flask, request, jsonify
import os
import requests
from supabase import create_client, Client

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/report", methods=["POST"])
def report():
    data = request.json
    username = data.get("username")
    user_id = data.get("user_id")
    job_id = data.get("job_id")

    if not username or not user_id or not job_id:
        return jsonify({"error": "Missing fields"}), 400

    # 🔹 Scriem în baza de date
    supabase.table("reports").insert({
        "username": username,
        "user_id": user_id,
        "job_id": job_id
    }).execute()

    # 🔹 Trimitem pe webhook
    payload = {
        "embeds": [
            {
                "title": "📡 New Report",
                "color": 3447003,
                "fields": [
                    {"name": "Username", "value": username, "inline": True},
                    {"name": "User ID", "value": str(user_id), "inline": True},
                    {"name": "Job ID", "value": job_id, "inline": False},
                ]
            }
        ]
    }
    requests.post(WEBHOOK_URL, json=payload)

    return jsonify({"status": "ok"}), 200


@app.route("/")
def home():
    return "Proxy is running!"
