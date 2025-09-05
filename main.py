from flask import Flask, request, jsonify
from supabase import create_client, Client
import os
import requests

# ========================
# Config
# ========================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Discord webhook pentru rapoarte

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# ========================
# Endpoint pentru element script
# ========================
@app.route("/report", methods=["POST"])
def report():
    try:
        data = request.json
        user_id = data.get("user_id")
        job_id = data.get("job_id")
        username = data.get("username")

        if not user_id or not job_id:
            return jsonify({"error": "Missing user_id or job_id"}), 400

        # Scriem în baza de date
        supabase.table("jobs").insert({
            "user_id": user_id,
            "job_id": job_id,
            "username": username
        }).execute()

        # Trimitem și pe webhook
        if WEBHOOK_URL:
            embed = {
                "title": "🎯 New Job Captured",
                "fields": [
                    {"name": "User ID", "value": str(user_id), "inline": True},
                    {"name": "Username", "value": str(username), "inline": True},
                    {"name": "Job ID", "value": str(job_id), "inline": False},
                ]
            }
            requests.post(WEBHOOK_URL, json={"embeds": [embed]})

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "✅ Element Proxy API is running!"


# ========================
# Run
# ========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
