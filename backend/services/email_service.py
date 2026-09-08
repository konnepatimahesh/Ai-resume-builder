
import secrets
from urllib.parse import urlparse

from flask import request
from flask_mail import Message

from database import db, mail
from models.resume_history import EmailToken


def send_verification_email(user):
    """
    Create an email verification token and send the verification email.
    """

    # Generate secure verification token
    token_str = secrets.token_urlsafe(32)

    # Save token in database
    record = EmailToken(
        user_id=user.id,
        token=token_str
    )

    db.session.add(record)
    db.session.commit()

    # ---------------------------------------------------------
    # Determine frontend URL
    # ---------------------------------------------------------

    # Default URL for local development
    origin = "http://localhost:5000"

    try:
        req_origin = request.headers.get("Origin") or request.referrer

        if req_origin:
            parsed = urlparse(req_origin)

            if parsed.scheme and parsed.netloc:
                origin = f"{parsed.scheme}://{parsed.netloc}"

    except Exception as e:
        print(f"[URL ERROR] Could not determine frontend URL: {e}")

    # Remove trailing slash if present
    origin = origin.rstrip("/")

    # Verification URL
    verify_url = f"{origin}/verify.html?token={token_str}"

    # ---------------------------------------------------------
    # Create email
    # ---------------------------------------------------------

    msg = Message(
        subject="Verify your ResumeAI account",
        recipients=[user.email],
        html=f"""
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

            <p style="
                color:#444;
                line-height:1.6;
            ">
                Thank you for creating an account with ResumeAI.
                Please verify your email address by clicking the
                button below.
            </p>

            <p style="
                color:#444;
                line-height:1.6;
            ">
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

            <p style="
                color:#888;
                font-size:13px;
                line-height:1.5;
            ">
                If you didn't create a ResumeAI account,
                you can safely ignore this email.
            </p>

            <p style="
                color:#aaa;
                font-size:12px;
                margin-top:24px;
            ">
                ResumeAI
            </p>

        </div>
        """,
    )

    # ---------------------------------------------------------
    # Send email
    # ---------------------------------------------------------

    print(f"[EMAIL] Sending verification email to {user.email}")
    print(f"[EMAIL] Verification URL: {verify_url}")

    try:
        # Flask-Mail uses the SMTP configuration from Flask config.
        # The connection timeout is controlled by Python/SMTP.
        mail.send(msg)

        print(f"[EMAIL] Verification email sent successfully to {user.email}")

    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email: {e}")

        # Remove the token if email could not be sent.
        try:
            db.session.delete(record)
            db.session.commit()
        except Exception as db_error:
            print(f"[TOKEN CLEANUP ERROR] {db_error}")

        # Re-raise so auth_service.py can handle the failure.
        raise
