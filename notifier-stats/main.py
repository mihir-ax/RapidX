import os
import smtplib
import requests
import random
import hashlib
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

# HARDCODE KAR DO YAHAN - Sirf yahi email address use hoga (For Normal Alerts)
FIXED_RECIPIENT = "mihir.rmx@gmail.com"

# --- PYDANTIC MODELS ---

class AlertData(BaseModel):
    subject: str
    tg_html_message: str
    email_html_message: str

class OTPRequest(BaseModel):
    app_name: str
    target_email: str

# --- ENDPOINTS ---

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


# ==========================================
# NEW FEATURE: SEND OTP
# ==========================================
@app.post("/send-otp")
def send_otp(data: OTPRequest):
    if not (GMAIL_ID and GMAIL_APP_PASS):
        return {"status": "FAILED", "message": "Gmail credentials missing."}

    # 1. Generate a 6-digit random OTP
    otp = str(random.randint(100000, 999999))
    
    # 2. Encrypt/Hash the OTP (SHA-256 is best for this)
    hashed_otp = hashlib.sha256(otp.encode()).hexdigest()

    # 3. Premium Professional HTML Template
    premium_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 0;">
        <div style="max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); overflow: hidden;">
            
            <!-- Header -->
            <div style="background-color: #4f46e5; padding: 30px 20px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600; letter-spacing: 1px;">{data.app_name}</h1>
            </div>
            
            <!-- Body -->
            <div style="padding: 40px 30px; text-align: center;">
                <h2 style="color: #333333; margin-top: 0; font-size: 22px;">Verify Your Email</h2>
                <p style="color: #666666; font-size: 16px; line-height: 1.5; margin-bottom: 30px;">
                    Hello! You requested a one-time password to access your account. Please use the verification code below to proceed.
                </p>
                
                <!-- OTP Box -->
                <div style="background-color: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 8px; padding: 20px; margin: 0 auto; width: fit-content;">
                    <span style="font-size: 36px; font-weight: bold; color: #0f172a; letter-spacing: 5px;">{otp}</span>
                </div>
                
                <p style="color: #94a3b8; font-size: 14px; margin-top: 30px;">
                    This code is valid for the next 10 minutes. If you did not request this, please ignore this email.
                </p>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #64748b; font-size: 12px; margin: 0;">
                    Securely sent by <strong>Alerify Auth Services</strong>
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    # 4. Prepare Email
    msg = EmailMessage()
    msg["Subject"] = f"{data.app_name} - Your Verification Code: {otp}"
    msg["From"] = f"{data.app_name} Auth <{GMAIL_ID}>"
    msg["To"] = data.target_email

    msg.set_content(f"Your {data.app_name} OTP is {otp}.") # Plain text fallback
    msg.add_alternative(premium_html, subtype="html") # Premium HTML

    # 5. Send Email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_ID, GMAIL_APP_PASS)
            smtp.send_message(msg)
            
        # Success Response (Returning Hash, not plain OTP)
        return {
            "status": "OK",
            "message": f"OTP successfully sent to {data.target_email}",
            "encrypted_otp": hashed_otp  # <--- Hashed OTP sending to your app
        }
    except Exception as e:
        return {
            "status": "FAILED",
            "error": f"Failed to send OTP: {str(e)}"
        }
