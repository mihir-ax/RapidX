import os
import time
import requests
from datetime import datetime

# 🌍 ENVIRONMENT VARIABLES
NEXUS_API_URL = os.getenv("NEXUS_API_URL", "https://your-nexus-app.vercel.app/api/uptime")
ALERIFY_API_URL = os.getenv("ALERIFY_API_URL", "https://your-alerify-app.onrender.com/send")

def fetch_targets():
    """Fetch live URLs to monitor directly from Nexus Database"""
    try:
        res = requests.get(f"{NEXUS_API_URL}?type=targets", timeout=10)
        if res.status_code == 200:
            return res.json().get('data', [])
    except Exception as e:
        print(f"Error fetching targets from Nexus: {e}")
    return []

def send_alert(target_name, target_url, error_msg):
    """Trigger Alerify if site is DOWN"""
    print(f"🚨 ALERT! {target_name} IS DOWN! Triggering Alerify...")
    
    html_msg = f"""
    <h3>🔴 UPTIME ALERT: SERVICE DOWN</h3>
    <p><b>Service:</b> {target_name}</p>
    <p><b>URL:</b> <a href="{target_url}">{target_url}</a></p>
    <p><b>Error:</b> {error_msg}</p>
    <p><b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """
    
    payload = {
        "subject": f"🔴 DOWN ALERT: {target_name}",
        "tg_html_message": html_msg,
        "email_html_message": html_msg
    }
    
    try:
        requests.post(ALERIFY_API_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to trigger Alerify: {e}")

def run_radar_sweep():
    targets = fetch_targets()
    if not targets:
        print(f"[{datetime.now()}] No targets found in Nexus. Sleeping...")
        return

    print(f"[{datetime.now()}] Initiating Radar Sweep for {len(targets)} targets...")
    
    for target in targets:
        start_time = time.time()
        status = "UP"
        latency = 0
        
        try:
            # PING THE URL
            res = requests.get(target["url"], timeout=15)
            latency = int((time.time() - start_time) * 1000)
            
            if res.status_code != 200:
                status = "DOWN"
                send_alert(target["name"], target["url"], f"HTTP Status {res.status_code}")
                
        except requests.exceptions.RequestException as e:
            # IF COMPLETELY DEAD/TIMEOUT
            latency = 9999
            status = "DOWN"
            send_alert(target["name"], target["url"], str(e))

        # SEND LOG BACK TO NEXUS FOR GRAPHING
        try:
            payload = {
                "action": "log_ping",
                "targetName": target["name"],
                "status": status,
                "latency": latency
            }
            requests.post(NEXUS_API_URL, json=payload, timeout=5)
            print(f"Logged: {target['name']} | Status: {status} | Latency: {latency}ms")
        except Exception as e:
            print(f"Failed to send log to Nexus: {e}")

if __name__ == "__main__":
    print("🤖 NEXUS Python Worker Node Started!")
    while True:
        run_radar_sweep()
        # Sleep for 5 Minutes (300 seconds)
        time.sleep(300)
