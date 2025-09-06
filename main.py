from flask import Flask, request, jsonify
import requests
from supabase import create_client
import os
from datetime import datetime

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/api/config", methods=["GET"])
def get_config():
    element_id = request.args.get("id")

    if not element_id:
        return jsonify({"error": "Missing id"}), 400

    data = supabase.table("elements").select("*").eq("id", element_id).execute()
    if not data.data:
        return jsonify({"error": "Config not found"}), 404

    return jsonify(data.data[0])


@app.route("/report", methods=["POST"])
def report():
    body = request.json
    element_id = body.get("id")
    job_id = body.get("jobId")

    if not element_id or not job_id:
        return jsonify({"error": "Missing fields"}), 400

    # caută config în DB
    data = supabase.table("elements").select("*").eq("id", element_id).execute()
    if not data.data:
        return jsonify({"error": "Invalid ID"}), 404

    config = data.data[0]
    webhook = config["webhook"]

    # update last_job_id în DB
    supabase.table("elements").update({
        "last_job_id": job_id,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", element_id).execute()

    # trimite pe webhook
    payload = {
        "content": f"🌐 Element Report\nID: `{element_id}`\nJobID: `{job_id}`"
    }
    try:
        r = requests.post(webhook, json=payload)
        if r.status_code == 204:
            return jsonify({"status": "ok", "to": "webhook"}), 200
        else:
            return jsonify({"status": "error", "webhook_response": r.text}), 500
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500
