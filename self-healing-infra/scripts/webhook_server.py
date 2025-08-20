from flask import Flask, request, jsonify
import subprocess, json, datetime, os, sys

app = Flask(__name__)

LOGFILE = "/var/log/self-heal.log"
PROJECT_DIR = os.environ.get("PROJECT_DIR", os.path.expanduser("~/self-healing-infra"))
WEBHOOK_SCRIPT = os.path.join(PROJECT_DIR, "scripts", "webhook.sh")

def log(line: str):
    os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)
    with open(LOGFILE, "a") as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {line}\n")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        log(f"Webhook payload: {json.dumps(payload)[:1000]}")
        # Execute the self-heal script
        env = os.environ.copy()
        env["PROJECT_DIR"] = PROJECT_DIR
        proc = subprocess.run(["/bin/bash", WEBHOOK_SCRIPT], capture_output=True, text=True, env=env)
        log(f"webhook.sh exit={proc.returncode}")
        if proc.stdout:
            log(proc.stdout[-1000:])
        if proc.stderr:
            log(proc.stderr[-1000:])
        status = 200 if proc.returncode == 0 else 500
        return jsonify({"status": "ok" if status == 200 else "error"}), status
    except Exception as e:
        log(f"Exception: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    app.run(host="0.0.0.0", port=port)
