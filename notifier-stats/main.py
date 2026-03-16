import os
import smtplib
import requests
from email.message import EmailMessage
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Alerify")

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

# HARDCODE KAR DO YAHAN - Sirf yahi email address use hoga
FIXED_RECIPIENT = "mihir.rmx@gmail.com"

class AlertData(BaseModel):
    subject: str
    tg_html_message: str
    email_html_message: str

@app.get("/")
def health_check():
    # Simple clean JSON response (No faltu HTML)
    return {
        "status": "OK",
        "message": "Alerify Running smoothly! 🚀",
        "fixed_email": FIXED_RECIPIENT
    }

@app.post("/send")
def send_alert(data: AlertData):
    errors = []

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
        msg["From"] = f"Bot Alerts <{GMAIL_ID}>"
        msg["To"] = FIXED_RECIPIENT

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
            "message": f"Alert successfully sent to Telegram & Email ({FIXED_RECIPIENT})",
        }
    else:
        return {
            "status": "PARTIAL_OK" if len(errors) == 1 else "FAILED",
            "errors": errors,
        }
