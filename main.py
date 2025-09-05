import os
import uuid
from flask import Flask, request, jsonify
from supabase import create_client, Client

# Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

# 🟢 Endpoint folosit de Element Script pentru raportare
@app.route("/report", methods=["POST"])
def report():
    data = request.json
    user_id = data.get("user_id")
    webhook = data.get("webhook")
    username = data.get("username")
    job_id = data.get("job_id")
    place_id = data.get("place_id")

    if not user_id or not webhook or not username or not job_id or not place_id:
        return jsonify({"error": "Missing fields"}), 400

    # Generăm un ID unic pentru script
    script_id = str(uuid.uuid4())

    # Salvăm în baza de date
    supabase.table("elements").insert({
        "id": script_id,
        "user_id": user_id,
        "webhook": webhook,
        "username": username,
        "job_id": job_id,
        "place_id": place_id
    }).execute()

    return jsonify({"message": "Reported successfully", "id": script_id})


# 🟢 Endpoint folosit de Autojoiner Script
@app.route("/get_job/<user_id>", methods=["GET"])
def get_job(user_id):
    result = supabase.table("elements").select("job_id, place_id").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
    if not result.data:
        return jsonify({"error": "No job found"}), 404
    return jsonify(result.data[0])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
