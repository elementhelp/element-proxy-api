import os
from flask import Flask, request, jsonify
from supabase import create_client, Client

# Config Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# ✅ Endpoint pentru raportare din scriptul Element
@app.route("/report", methods=["POST"])
def report():
    try:
        data = request.json
        user_id = data.get("user_id")
        job_id = data.get("job_id")
        place_id = data.get("place_id")
        webhook = data.get("webhook")
        username = data.get("username")

        if not (user_id and job_id and place_id):
            return jsonify({"error": "Missing required fields"}), 400

        # Inserăm raportul în tabel
        result = supabase.table("elements").insert({
            "user_id": user_id,
            "job_id": job_id,
            "place_id": place_id,
            "webhook": webhook,
            "username": username
        }).execute()

        return jsonify({"success": True, "inserted": result.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Endpoint pentru Autojoiner
@app.route("/get_job", methods=["GET"])
def get_job():
    try:
        user_id = request.args.get("user_id")

        query = supabase.table("elements").select("job_id, place_id").order("created_at", desc=True).limit(1)

        # Dacă Autojoiner-ul cere pentru un user anume
        if user_id:
            query = query.eq("user_id", user_id)

        result = query.execute()

        if not result.data:
            return jsonify({"error": "No job found"}), 404

        return jsonify(result.data[0])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "✅ API activ pentru Element & Autojoiner!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
