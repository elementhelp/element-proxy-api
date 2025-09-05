import os
from flask import Flask, request, jsonify
from supabase import create_client, Client

# ==============================
# 🔧 Configurare Supabase
# ==============================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==============================
# 🚀 Flask App
# ==============================
app = Flask(__name__)

# ==============================
# 🟢 Health Check
# ==============================
@app.route("/")
def home():
    return jsonify({"status": "running"}), 200

# ==============================
# 📌 Report Job (folosit de element.lua)
# ==============================
@app.route("/report_job", methods=["POST"])
def report_job():
    data = request.json
    if not data or "id" not in data:
        return jsonify({"error": "Missing id"}), 400

    try:
        supabase.table("elements").update({
            "job_id": data.get("job_id"),
            "place_id": data.get("place_id"),
            "custom_username": data.get("username")
        }).eq("id", data["id"]).execute()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"})

# ==============================
# 📌 Get Job (folosit de autojoiner.lua)
# ==============================
@app.route("/get_job", methods=["GET"])
def get_job():
    element_id = request.args.get("id")
    if not element_id:
        return jsonify({"error": "Missing id"}), 400

    try:
        result = supabase.table("elements").select("job_id, place_id").eq("id", element_id).execute()
        if not result.data or len(result.data) == 0:
            return jsonify({"error": "No job found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(result.data[0])

# ==============================
# ▶️ Run App
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
