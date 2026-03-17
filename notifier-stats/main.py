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
<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><style>
@media (prefers-color-scheme: dark) {{
    body {{
        background-color: #111111 !important;
    }}
    .container {{
        background-color: #1a1a1a !important;
    }}
    .text {{
        color: #eeeeee !important;
    }}
    .subtext {{
        color: #bbbbbb !important;
    }}
    .otp-box {{
        background-color: #2a2a2a !important;
        color: #ffffff !important;
    }}
    .footer {{
        background-color: #161616 !important;
        color: #aaaaaa !important;
    }}
}}
</style>
</head>
<body style="margin:0; padding:0; background:#f4f4f4; font-family: Arial, sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" bgcolor="#f4f4f4">
<tr>
<td align="center">
    <table width="100%" cellpadding="0" cellspacing="0" bgcolor="#ffffff" 
           style="max-width:480px;" class="container">
        <tr>
            <td align="center" style="padding:25px 20px 10px 20px;">
                                <img src="https://via.placeholder.com/60"
                     width="60"
                     height="60"
                     alt="Logo"
                     style="display:block; margin-bottom:10px;">
                <h1 style="margin:0; font-size:20px; color:#111;" class="text">
                    {data.app_name}
                </h1>
            </td>
        </tr>
        <tr>
            <td height="1" bgcolor="#eaeaea"></td>
        </tr>
        <tr>
            <td align="center" style="padding:30px 20px;">
                <h2 style="margin:0 0 10px 0; font-size:18px; color:#222;" class="text">
                    Verify your email
                </h2>
                <p style="font-size:14px; color:#666; line-height:1.5; margin:0 0 25px 0;" class="subtext">
                    Use the verification code below to continue.
                </p>
                <table cellpadding="0" cellspacing="0" align="center">
                    <tr>
                        <td align="center" bgcolor="#f0f0f0" 
                            style="padding:12px 20px; font-size:24px; font-weight:bold; letter-spacing:4px; color:#111;"
                            class="otp-box">
                            {otp}
                        </td>
                    </tr>
                </table>
                <p style="font-size:12px; color:#999; margin:20px 0 0 0;" class="subtext">
                    This code expires in 10 minutes.
                </p>
            </td>
        </tr>
        <tr>
            <td align="center" bgcolor="#fafafa" 
                style="padding:20px; border-top:1px solid #eaeaea;" 
                class="footer">
                <p style="margin:0; font-size:12px; color:#888;">
                    If you didn’t request this, you can ignore this email.
                </p>
            </td>
        </tr>
    </table>
</td>
</tr>
</table>
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
