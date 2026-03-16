import os
import smtplib
import requests
from email.message import EmailMessage
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Create the FastAPI app
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


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Alertifer - Notification System</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; color: white; }
            .container { background: rgba(255,255,255,0.95); border-radius: 10px; padding: 30px; max-width: 800px; margin: 0 auto; color: #333; }
            h1 { color: #667eea; }
            .status { background: #48bb78; color: white; padding: 10px; border-radius: 5px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Alertifer</h1>
            <div class="status">✅ System Operational</div>
            <p>Welcome to Alertifer - Your notification API for Email & Telegram alerts!</p>
            <p>📧 Fixed Recipient: mihir.rmx@gmail.com</p>
            <p>📱 <a href="/start">Quick Start Guide</a> | <a href="/health">Health Check</a></p>
        </div>
    </body>
    </html>
    """


@app.get("/start", response_class=HTMLResponse)
async def start():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Alertifer - Quick Start</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f0f4f8; margin: 0; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            pre { background: #333; color: white; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📘 Alertifer Quick Start</h1>
            <p>Send alerts using this Python code:</p>
            <pre>
import requests

response = requests.post("https://your-app.vercel.app/send", json={
    "subject": "Test Alert",
    "tg_html_message": "&lt;b&gt;Test&lt;/b&gt; message",
    "email_html_message": "&lt;h1&gt;Test&lt;/h1&gt;"
})
print(response.json())
            </pre>
            <p><a href="/">← Back to Home</a></p>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "service": "Alertifer",
        "recipient": FIXED_RECIPIENT,
        "telegram_configured": bool(TG_BOT_TOKEN and TG_OWNER_ID),
        "email_configured": bool(GMAIL_ID and GMAIL_APP_PASS)
    }


@app.post("/send")
async def send_alert(data: AlertData):
    errors = []
    target_email = FIXED_RECIPIENT

    # Send Telegram
    if TG_BOT_TOKEN and TG_OWNER_ID:
        try:
            tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
            tg_text = f"<b>🚨 {data.subject}</b>\n\n{data.tg_html_message}"
            tg_resp = requests.post(tg_url, json={
                "chat_id": TG_OWNER_ID,
                "text": tg_text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }, timeout=10)
            if tg_resp.status_code != 200:
                errors.append(f"Telegram Error: {tg_resp.text}")
        except Exception as e:
            errors.append(f"Telegram Exception: {str(e)}")
    else:
        errors.append("Telegram credentials missing")

    # Send Email
    if GMAIL_ID and GMAIL_APP_PASS:
        try:
            msg = EmailMessage()
            msg["Subject"] = data.subject
            msg["From"] = f"Alertifer <{GMAIL_ID}>"
            msg["To"] = target_email
            msg.set_content("Please enable HTML to view this email.")
            msg.add_alternative(data.email_html_message, subtype="html")
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(GMAIL_ID, GMAIL_APP_PASS)
                smtp.send_message(msg)
        except Exception as e:
            errors.append(f"Email Exception: {str(e)}")
    else:
        errors.append("Gmail credentials missing")

    if len(errors) == 0:
        return {"status": "OK", "service": "Alertifer", "message": f"Alert sent to {target_email}"}
    else:
        return {"status": "FAILED", "service": "Alertifer", "errors": errors}
