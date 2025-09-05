import os
from flask import Flask, request, jsonify
from supabase import create_client, Client

# ---------------------------
# CONFIG
# ---------------------------
app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------------------------
# /report → called by Element Script (Roblox)
# ---------------------------
@app.route("/report", methods=["POST"])
def report():
    data = request.get_json()

    element_id = data.get("id")
    key = data.get("key")
    job_id = data.get("job_id")
    place_id = data.get("place_id")

    if not element_id or not key or not job_id or not place_id:
        return jsonify({"error": "Missing fields"}), 400

    # Verify element_id exists
    existing = supabase.table("elements").select("id, key").eq("id", element_id).execute()
    if not existing.data:
        return jsonify({"error": "Invalid ID"}), 404

    element = existing.data[0]

    # Check KEY
    if element["key"] != key:
        return jsonify({"error": "Invalid KEY"}), 403

    # Update job info
    supabase.table("elements").update({
        "last_job_id": job_id,
        "last_place_id": place_id
    }).eq("id", element_id).execute()

    return jsonify({"status": "ok", "message": "Job reported"}), 200


# ---------------------------
# /get_job → called by Autojoiner Script (Roblox)
# ---------------------------
@app.route("/get_job", methods=["POST"])
def get_job():
    data = request.get_json()

    element_id = data.get("id")
    key = data.get("key")

    if not element_id or not key:
        return jsonify({"error": "Missing fields"}), 400

    # Verify element_id exists
    existing = supabase.table("elements").select(
        "id, key, last_job_id, last_place_id"
    ).eq("id", element_id).execute()

    if not existing.data:
        return jsonify({"error": "Invalid ID"}), 404

    element = existing.data[0]

    # Check KEY
    if element["key"] != key:
        return jsonify({"error": "Invalid KEY"}), 403

    # Check if job exists
    if not element.get("last_job_id"):
        return jsonify({"error": "No job reported yet"}), 404

    return jsonify({
        "job_id": element["last_job_id"],
        "place_id": element["last_place_id"]
    }), 200


# ---------------------------
# Health check (optional)
# ---------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running"}), 200


# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
