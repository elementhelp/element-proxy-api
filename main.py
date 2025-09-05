from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Exemplu: Supabase sau DB-ul tău
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Aici doar simulăm partea de salvare și citire job_id
DATABASE = {}  # (înlocuiești cu supabase ulterior)

@app.route("/report", methods=["POST"])
def report():
    data = request.json
    user_id = data.get("user_id")
    job_id = data.get("job_id")
    webhook = data.get("webhook")

    if not user_id or not job_id:
        return jsonify({"error": "Missing fields"}), 400

    # Salvăm job_id în DB fake
    DATABASE[user_id] = job_id

    # Trimitem pe webhook
    if webhook:
        try:
            requests.post(webhook, json={
                "content": f"👤 User `{user_id}` este într-un server.\n🆔 Job ID: `{job_id}`"
            })
        except Exception as e:
            print("Webhook error:", e)

    return jsonify({"status": "ok", "job_id": job_id})


@app.route("/get-job/<user_id>", methods=["GET"])
def get_job(user_id):
    job_id = DATABASE.get(user_id)
    if not job_id:
        return jsonify({"error": "Job not found"}), 404

    return jsonify({"job_id": job_id})


@app.route("/")
def home():
    return "✅ Element Proxy API is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
