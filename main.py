from flask import Flask, request, jsonify
from supabase import create_client
import requests
import os

app = Flask(__name__)

# --- Config Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/report", methods=["POST"])
def report():
    try:
        data = request.json
        key = data.get("key")
        job_id = data.get("job_id")
        place_id = data.get("place_id")

        if not key:
            return jsonify({"error": "Missing key"}), 400

        # 1. Actualizează datele în baza de date
        supabase.table("elements").update({
            "last_job_id": job_id,
            "last_place_id": place_id
        }).eq("id", key).execute()

        # 2. Ia webhook-ul din DB
        result = supabase.table("elements").select("webhook").eq("id", key).single().execute()

        if result.data and result.data.get("webhook"):
            webhook_url = result.data["webhook"]

            # 3. Trimite mesaj pe Discord
            payload = {
                "embeds": [{
                    "title": "📡 New Element Report",
                    "description": f"**Key:** `{key}`\n**Job ID:** `{job_id}`\n**Place ID:** `{place_id}`",
                    "color": 0x00ffcc
                }]
            }

            try:
                r = requests.post(webhook_url, json=payload, timeout=10)
                if r.status_code != 204:  # Discord răspunde cu 204 la succes
                    print(f"[ERROR] Webhook response: {r.status_code} {r.text}")
            except Exception as e:
                print(f"[ERROR] Could not send webhook: {e}")

        else:
            print(f"[WARN] No webhook set for key {key}")

        return jsonify({"status": "ok"})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
