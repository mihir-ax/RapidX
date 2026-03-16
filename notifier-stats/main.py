import os
import smtplib
import requests
from email.message import EmailMessage
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Alertifer API - Mail & Telegram Alerts")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment Variables
GMAIL_ID = os.getenv("GMAIL_ID")
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_OWNER_ID = os.getenv("TG_OWNER_ID")
FIXED_RECIPIENT = "mihir.rmx@gmail.com"


class AlertData(BaseModel):
    subject: str
    tg_html_message: str
    email_html_message: str
    # to_email: str = None   # Isko comment out kar diya ya hata diya


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Alertifer - Notification System</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                max-width: 800px;
                margin: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                color: #333;
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .badge {
                background: #764ba2;
                color: white;
                padding: 5px 15px;
                border-radius: 50px;
                display: inline-block;
                margin-bottom: 20px;
                font-size: 0.9em;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .feature-card h3 {
                margin-top: 0;
                color: #667eea;
            }
            .endpoint {
                background: #2d3748;
                color: #e2e8f0;
                padding: 15px;
                border-radius: 8px;
                font-family: monospace;
                margin: 10px 0;
            }
            .status {
                display: inline-block;
                padding: 8px 16px;
                background: #48bb78;
                color: white;
                border-radius: 20px;
                font-weight: bold;
            }
            .footer {
                margin-top: 30px;
                text-align: center;
                color: #718096;
                font-size: 0.9em;
            }
            a {
                color: #667eea;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Alertifer</h1>
            <div class="badge">Mail & Telegram Notification System</div>
            
            <p>Welcome to <strong>Alertifer</strong> - Your reliable notification API for sending alerts via Email and Telegram!</p>
            
            <div class="status">✅ System Status: Operational</div>
            
            <div class="features">
                <div class="feature-card">
                    <h3>📧 Email Notifications</h3>
                    <p>Send beautiful HTML emails with full CSS support to your fixed recipient.</p>
                </div>
                <div class="feature-card">
                    <h3>📱 Telegram Alerts</h3>
                    <p>Get instant Telegram messages with HTML formatting support.</p>
                </div>
                <div class="feature-card">
                    <h3>🔒 Secure</h3>
                    <p>Environment variables for credentials, CORS enabled for all origins.</p>
                </div>
            </div>

            <h2>📡 API Endpoints</h2>
            
            <div class="endpoint">
                <strong>GET /</strong> - Welcome page (you're here!)
            </div>
            
            <div class="endpoint">
                <strong>GET /start</strong> - Quick start guide & API information
            </div>
            
            <div class="endpoint">
                <strong>POST /send</strong> - Send alerts (JSON payload)<br>
                <small style="color: #a0aec0;">{
                    "subject": "Your Subject",
                    "tg_html_message": "Telegram message with HTML",
                    "email_html_message": "Full HTML email content"
                }</small>
            </div>

            <h2>⚡ Quick Example</h2>
            <div class="endpoint" style="background: #1a202c;">
                curl -X POST https://rapid-x-chi.vercel.app/send \<br>
                &nbsp;&nbsp;-H "Content-Type: application/json" \<br>
                &nbsp;&nbsp;-d '{
                    "subject": "Test Alert",
                    "tg_html_message": "Bot is <b>online</b>",
                    "email_html_message": "&lt;h1&gt;Test&lt;/h1&gt;"
                }'
            </div>
            
            <div class="footer">
                <p>🔔 Configured to send alerts to: <strong>mihir.rmx@gmail.com</strong></p>
                <p>📅 2025 Alertifer - All rights reserved</p>
                <p><a href="#">Documentation</a> | <a href="#">GitHub</a> | <a href="#">Support</a></p>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/start", response_class=HTMLResponse)
def start():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Alertifer - Quick Start</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; }
            h2 { color: #34495e; border-bottom: 2px solid #eee; padding-bottom: 10px; }
            code {
                background: #f8f9fa;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                color: #e83e8c;
            }
            pre {
                background: #2d3748;
                color: #e2e8f0;
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
            }
            .step {
                background: #f8f9fa;
                border-left: 4px solid #4CAF50;
                padding: 15px;
                margin: 15px 0;
                border-radius: 0 8px 8px 0;
            }
            .note {
                background: #fff3cd;
                border: 1px solid #ffeeba;
                padding: 15px;
                border-radius: 8px;
                color: #856404;
            }
            .btn {
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin: 10px 5px 10px 0;
            }
            .btn:hover {
                background: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Alertifer - Quick Start Guide</h1>
            <p>Get started with Alertifer in 3 simple steps!</p>
            
            <div class="step">
                <h3>📌 Step 1: Install Required Library</h3>
                <pre>pip install requests</pre>
            </div>
            
            <div class="step">
                <h3>📌 Step 2: Create Your Alert Script</h3>
                <p>Create a Python file (e.g., <code>send_alert.py</code>):</p>
                <pre>import requests

API_URL = "https://rapid-x-chi.vercel.app/send"

payload = {
    "subject": "System Warning",
    
    # For Telegram (basic HTML tags only)
    "tg_html_message": "Bot is <b>Offline</b>. Please check the <code>server</code>.",
    
    # For Email (full HTML with CSS)
    "email_html_message": """
    &lt;html&gt;
        &lt;body style="font-family: Arial; background-color: #f4f4f4; padding: 20px;"&gt;
            &lt;div style="background-color: white; padding: 20px; border-radius: 10px;"&gt;
                &lt;h2 style="color: #667eea;"&gt;🚨 System Warning&lt;/h2&gt;
                &lt;p&gt;Your bot is currently offline.&lt;/p&gt;
            &lt;/div&gt;
        &lt;/body&gt;
    &lt;/html&gt;
    """
}

response = requests.post(API_URL, json=payload)
print(response.json())</pre>
            </div>
            
            <div class="step">
                <h3>📌 Step 3: Run Your Script</h3>
                <pre>python send_alert.py</pre>
                <p>Expected response:</p>
                <pre>{
    "status": "OK",
    "message": "Alert successfully sent to Telegram & Email (mihir.rmx@gmail.com)"
}</pre>
            </div>
            
            <h2>📚 API Reference</h2>
            
            <h3>POST /send</h3>
            <p><strong>Request Body:</strong></p>
            <pre>{
    "subject": "string",              # Alert subject/title
    "tg_html_message": "string",       # Telegram message with HTML
    "email_html_message": "string"      # Full HTML email content
}</pre>

            <p><strong>Response:</strong></p>
            <pre>{
    "status": "OK|PARTIAL_OK|FAILED",
    "message": "Success message",      # Only if status is OK
    "errors": []                       # Only if there are errors
}</pre>

            <div class="note">
                <strong>📝 Note:</strong> All alerts are sent to the fixed email: <code>mihir.rmx@gmail.com</code>
            </div>
            
            <h2>🎯 Example Use Cases</h2>
            <ul>
                <li>System monitoring alerts</li>
                <li>Server downtime notifications</li>
                <li>Automated task completion reports</li>
                <li>Security breach warnings</li>
                <li>Daily/weekly summary reports</li>
            </ul>
            
            <a href="/" class="btn">🏠 Back to Home</a>
            <a href="#" class="btn">📖 Full Documentation</a>
            <a href="#" class="btn">🐛 Report Bug</a>
        </div>
    </body>
    </html>
    """


@app.get("/health")
def health_check():
    return {
        "status": "OK",
        "service": "Alertifer",
        "message": "Mail & TG Alert API is Running smoothly! 🚀",
        "recipient": FIXED_RECIPIENT,
        "telegram_configured": bool(TG_BOT_TOKEN and TG_OWNER_ID),
        "email_configured": bool(GMAIL_ID and GMAIL_APP_PASS)
    }


@app.post("/send")
def send_alert(data: AlertData):
    errors = []
    target_email = FIXED_RECIPIENT

    # ==========================================
    # 1. SEND TELEGRAM MESSAGE
    # ==========================================
    if TG_BOT_TOKEN and TG_OWNER_ID:
        tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        tg_text = f"<b>🚨 {data.subject}</b>\n\n{data.tg_html_message}"

        try:
            tg_resp = requests.post(
                tg_url,
                json={
                    "chat_id": TG_OWNER_ID,
                    "text": tg_text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=10,
            )
            if tg_resp.status_code != 200:
                errors.append(f"Telegram Error: {tg_resp.text}")
        except Exception as e:
            errors.append(f"Telegram Exception: {str(e)}")
    else:
        errors.append("Telegram credentials missing in env variables.")

    # ==========================================
    # 2. SEND GMAIL MESSAGE - HARDCODED RECIPIENT
    # ==========================================
    if GMAIL_ID and GMAIL_APP_PASS:
        msg = EmailMessage()
        msg["Subject"] = data.subject
        msg["From"] = f"Alertifer <{GMAIL_ID}>"
        msg["To"] = target_email

        # Fallback for old devices
        msg.set_content("Please enable HTML to view this email.")
        # Main HTML content
        msg.add_alternative(data.email_html_message, subtype="html")

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(GMAIL_ID, GMAIL_APP_PASS)
                smtp.send_message(msg)
        except Exception as e:
            errors.append(f"Email Exception: {str(e)}")
    else:
        errors.append("Gmail credentials missing in env variables.")

    # ==========================================
    # 3. RETURN FINAL RESPONSE
    # ==========================================
    if len(errors) == 0:
        return {
            "status": "OK",
            "service": "Alertifer",
            "message": f"Alert successfully sent to Telegram & Email ({target_email})",
        }
    else:
        return {
            "status": "PARTIAL_OK" if len(errors) == 1 else "FAILED",
            "service": "Alertifer",
            "errors": errors,
        }
