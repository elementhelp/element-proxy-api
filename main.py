import os
from flask import Flask, request, Response, jsonify
from supabase import create_client, Client

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# CDN ENDPOINT - ELEMENT SCRIPT
# -------------------------------
@app.get("/cdn/element.luau")
def serve_element():
    user_id = request.args.get("id")
    if not user_id:
        return Response("-- Missing ID", mimetype="text/plain")

    row = supabase.table("elements").select("id, webhook").eq("user_id", user_id).single().execute()
    if not row.data:
        return Response("-- No data found", mimetype="text/plain")

    element_id = row.data["id"]
    webhook = row.data.get("webhook", "")

    with open("scripts/element_template.luau", "r") as f:
        code = f.read()

    code = code.replace("{ID}", element_id).replace("{WEBHOOK}", webhook)
    return Response(code, mimetype="text/plain")

# -------------------------------
# CDN ENDPOINT - AUTOJOINER SCRIPT
# -------------------------------
@app.get("/cdn/autojoiner.luau")
def serve_autojoiner():
    key = request.args.get("key")
    if not key:
        return Response("-- Missing KEY", mimetype="text/plain")

    with open("scripts/autojoiner_template.luau", "r") as f:
        code = f.read()

    code = code.replace("{KEY}", key)
    return Response(code, mimetype="text/plain")

# -------------------------------
# API ENDPOINT - GET JOB
# -------------------------------
@app.get("/get_job")
def get_job():
    key = request.args.get("key")
    if not key:
        return jsonify({"error": "Missing key"}), 400

    row = (
        supabase.table("jobs")
        .select("jobId, placeId")
        .eq("key", key)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not row.data:
        return jsonify({"error": "No job found"}), 404

    return jsonify(row.data[0])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
