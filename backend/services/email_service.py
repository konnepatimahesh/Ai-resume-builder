import os
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlparse
from flask import request
from flask_mail import Message
from database import db, mail
from models.resume_history import EmailToken


def send_verification_email(user):
    """
    Create an email verification token and send the verification email using Flask-Mail.
    """
    token_str = secrets.token_urlsafe(32)

    record = EmailToken(
        user_id=user.id,
        token=token_str,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )

    db.session.add(record)
    db.session.commit()

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "https://ai-resume-builder-frontend-sarl.onrender.com"
    ).rstrip("/")

    try:
        req_origin = request.headers.get("Origin") or request.referrer
        if req_origin:
            parsed = urlparse(req_origin)
            if parsed.scheme and parsed.netloc:
                frontend_url = f"{parsed.scheme}://{parsed.netloc}"
    except Exception as e:
        print(f"[URL ERROR] Could not determine frontend URL: {e}")

    verify_url = f"{frontend_url}/verify.html?token={token_str}"

    sender = os.getenv("MAIL_USERNAME") or "konnepatimahesh@gmail.com"

    html = f"""
    <div style="
        font-family: Arial, sans-serif;
        max-width: 520px;
        margin: auto;
        padding: 32px;
        background-color: #ffffff;
    ">
        <h2 style="color:#4f46e5;">
            Welcome to ResumeAI, {user.name}!
        </h2>

        <p style="color:#444;line-height:1.6;">
            Thank you for creating an account with ResumeAI.
            Please verify your email address by clicking the button below.
        </p>

        <p style="color:#444;line-height:1.6;">
            This verification link expires in 24 hours.
        </p>

        <a href="{verify_url}"
           style="
               display:inline-block;
               margin:24px 0;
               padding:12px 28px;
               background:#4f46e5;
               color:#ffffff;
               border-radius:8px;
               text-decoration:none;
               font-weight:600;
           ">
            Verify Email
        </a>

        <p style="color:#888;font-size:13px;line-height:1.5;">
            If you didn't create a ResumeAI account, you can safely ignore this email.
        </p>

        <p style="color:#aaa;font-size:12px;margin-top:24px;">
            ResumeAI
        </p>
    </div>
    """

    try:
        print(f"[EMAIL] Preparing verification email for {user.email}")
        print(f"[EMAIL] Verification URL: {verify_url}")

        msg = Message(
            subject="Verify your ResumeAI account",
            sender=sender,
            recipients=[user.email],
            html=html
        )

        mail.send(msg)
        print(f"[EMAIL] Verification email sent successfully to {user.email}")

    except Exception as e:
        print(f"[EMAIL ERROR] Flask-Mail failed: {e}")

        try:
            db.session.delete(record)
            db.session.commit()
            print("[EMAIL] Verification token removed.")
        except Exception as db_error:
            db.session.rollback()
            print(f"[TOKEN CLEANUP ERROR] {db_error}")

        raise