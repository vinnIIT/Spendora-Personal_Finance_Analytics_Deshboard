import smtplib
import os
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

def send_otp_email(receiver_email, otp, user_name="User"):

    sender_email = os.getenv("EMAIL_USER")
    app_password = os.getenv("EMAIL_PASS")

    if not sender_email or not app_password:
        st.error("Email credentials not found.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Spendora - Email Verification Code"
    msg["From"] = f"Spendora <{sender_email}>"
    msg["To"] = receiver_email

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color:#f4f6f9; padding:20px;">
        <div style="max-width:520px; margin:auto; background:white; padding:30px; border-radius:12px;">
            <h2 style="color:#1E3A8A;">💰 Spendora</h2>
            <p>Hello! <b>{user_name}</b>,</p>
            <p>Welcome to Vineet's iconic project!</p>
            <p>We received a request to verify your email address.</p>
            <p>Your OTP:</p>
            <div style="font-size:28px;font-weight:bold;letter-spacing:6px;text-align:center;background:#F1F5F9;padding:15px;border-radius:8px;margin:20px 0;">
                {otp}
            </div>
            <p>This OTP is valid for 5 minutes.</p>
            <hr>
            <p style="font-size:12px;color:#6B7280;">
                © {datetime.datetime.now().year} Spendora
            </p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())