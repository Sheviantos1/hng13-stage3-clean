import os
import time
import requests
from collections import deque

LOG_PATH = "/var/log/nginx/access.log"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
ERROR_RATE_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", 2))
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", 200))
ALERT_COOLDOWN_SEC = int(os.getenv("ALERT_COOLDOWN_SEC", 300))
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"

last_pool = None
last_alert_time = 0
error_window = deque(maxlen=WINDOW_SIZE)

def send_alert(message):
    global last_alert_time
    if MAINTENANCE_MODE or time.time() - last_alert_time < ALERT_COOLDOWN_SEC:
        return
    requests.post(SLACK_WEBHOOK_URL, json={"text": message})
    last_alert_time = time.time()

def parse_log_line(line):
    parts = line.split(" ")
    pool = next((p.split("=")[1] for p in parts if p.startswith("pool=")), None)
    status = next((s.split("=")[1] for s in parts if s.startswith("upstream_status=")), None)
    return pool, status

def watch_logs():
    global last_pool
    with open(LOG_PATH, "r") as f:
        f.seek(0, 2)  # Go to end of file
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            pool, status = parse_log_line(line)
            if pool and pool != last_pool and pool != "-":
                send_alert(f"⚠️ Failover detected: {last_pool} → {pool}")
                last_pool = pool
            if status and (status.startswith("4") or status.startswith("5")):
                error_window.append(1)
            else:
                error_window.append(0)
            error_rate = sum(error_window) / len(error_window) * 100
            if error_rate > ERROR_RATE_THRESHOLD:
                send_alert(f"🚨 Shevy Alert 🚨\nError rate: {error_rate:.2f}% over the last {WINDOW_SIZE} seconds\nMaintenance mode: {MAINTENANCE_MODE}")



if __name__ == "__main__":
    watch_logs()