import os
import time
import requests
from datetime import datetime
from flask import Flask, jsonify
from threading import Thread

app = Flask(__name__)

# 🌍 ENVIRONMENT VARIABLES
NEXUS_API_URL = os.getenv("NEXUS_API_URL", "https://nexus-lemon-beta.vercel.app/api/uptime")
ALERIFY_API_URL = os.getenv("ALERIFY_API_URL", "https://rapid-x-chi.vercel.app/send")

# Track consecutive failures for each target
consecutive_failures = {}

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
    """Trigger Alerify if site is DOWN for 3 consecutive checks"""
    print(f"🚨 ALERT! {target_name} IS DOWN FOR 3 CONSECUTIVE CHECKS! Triggering Alerify...")
    
    html_msg = f"""
    <h3>🔴 UPTIME ALERT: SERVICE DOWN</h3>
    <p><b>Service:</b> {target_name}</p>
    <p><b>URL:</b> <a href='{target_url}'>{target_url}</a></p>
    <p><b>Error:</b> {error_msg}</p>
    <p><b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><b>Note:</b> Alert triggered after 3 consecutive failed checks</p>
    """
    
    payload = {
        "subject": f"🔴 DOWN ALERT: {target_name}",
        "tg_html_message": html_msg,
        "email_html_message": html_msg
    }
    
    try:
        requests.post(ALERIFY_API_URL, json=payload, timeout=10)
        print(f"✅ Alert sent for {target_name}")
    except Exception as e:
        print(f"Failed to trigger Alerify: {e}")

def run_radar_sweep():
    global consecutive_failures
    targets = fetch_targets()
    if not targets:
        print(f"[{datetime.now()}] No targets found in Nexus. Sleeping...")
        return

    print(f"[{datetime.now()}] Initiating Radar Sweep for {len(targets)} targets...")
    
    for target in targets:
        start_time = time.time()
        status = "UP"
        latency = 0
        target_name = target["name"]
        target_url = target["url"]
        
        try:
            # PING THE URL
            res = requests.get(target_url, timeout=15)
            latency = int((time.time() - start_time) * 1000)
            
            if res.status_code != 200:
                status = "DOWN"
                # Track consecutive failures
                consecutive_failures[target_name] = consecutive_failures.get(target_name, 0) + 1
                print(f"⚠️ {target_name} DOWN #{consecutive_failures[target_name]} | Status: {res.status_code}")
                
                # Send alert only after 3 consecutive failures
                if consecutive_failures[target_name] >= 3:
                    send_alert(target_name, target_url, f"HTTP Status {res.status_code}")
                    # Reset after sending alert to avoid spam (optional)
                    consecutive_failures[target_name] = 0
            else:
                # If UP, reset consecutive failures
                if consecutive_failures.get(target_name, 0) > 0:
                    print(f"✅ {target_name} is back UP! Resetting failure counter")
                consecutive_failures[target_name] = 0
                
        except requests.exceptions.RequestException as e:
            # IF COMPLETELY DEAD/TIMEOUT
            latency = 9999
            status = "DOWN"
            # Track consecutive failures
            consecutive_failures[target_name] = consecutive_failures.get(target_name, 0) + 1
            print(f"⚠️ {target_name} DOWN #{consecutive_failures[target_name]} | Error: {str(e)}")
            
            # Send alert only after 3 consecutive failures
            if consecutive_failures[target_name] >= 3:
                send_alert(target_name, target_url, str(e))
                # Reset after sending alert to avoid spam (optional)
                consecutive_failures[target_name] = 0

        # SEND LOG BACK TO NEXUS FOR GRAPHING
        try:
            payload = {
                "action": "log_ping",
                "targetName": target_name,
                "status": status,
                "latency": latency
            }
            requests.post(NEXUS_API_URL, json=payload, timeout=5)
            print(f"Logged: {target_name} | Status: {status} | Latency: {latency}ms")
        except Exception as e:
            print(f"Failed to send log to Nexus: {e}")

def background_worker():
    """Background thread to run radar sweeps continuously"""
    print("🤖 NEXUS Python Worker Node Started!")
    while True:
        run_radar_sweep()
        # Sleep for 5 Minutes (300 seconds)
        time.sleep(60)

@app.route('/')
def health_check():
    """Root endpoint for Render to verify service is alive"""
    return jsonify({
        "status": "I AM ALIVE",
        "message": "Nexus Uptime Monitor Worker is running",
        "timestamp": datetime.now().isoformat(),
        "monitored_targets": len(consecutive_failures),
        "active_alerts": {k: v for k, v in consecutive_failures.items() if v > 0}
    }), 200

@app.route('/ping')
def ping():
    """Simple ping endpoint for quick checks"""
    return jsonify({
        "status": "success",
        "message": "pong",
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == "__main__":
    # Start the background monitoring thread
    worker_thread = Thread(target=background_worker, daemon=True)
    worker_thread.start()
    
    # Start Flask web server
    port = int(os.getenv("PORT", 5000))
    print(f"🌐 Web service running on port {port}")
    # Removed localhost print - ab sirf port dikhega
    
    app.run(host='0.0.0.0', port=port)
