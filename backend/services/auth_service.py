
from database import db
from models.user import User
from models.resume_history import EmailToken
from services.email_service import send_verification_email


def register_user(name, email, password):
    email = email.lower().strip()

    # Check whether the email is already registered
    if User.query.filter_by(email=email).first():
        return None, "Email already registered."

    # Create user
    user = User(
        name=name.strip(),
        email=email
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Send verification email
    try:
        send_verification_email(user)
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

        # Remove the newly created user if email sending fails
        db.session.delete(user)
        db.session.commit()

        return None, "Unable to send verification email. Please try again later."

    return user, None


def verify_token(token_str):
    record = EmailToken.query.filter_by(token=token_str).first()

    if not record:
        return None, "Invalid or expired link."

    user = User.query.get(record.user_id)

    if not user:
        return None, "User not found."

    user.is_verified = True

    db.session.delete(record)
    db.session.commit()

    return user, None


def authenticate(email, password):
    email = email.lower().strip()

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return None, "Invalid email or password."

    if not user.is_verified:
        return None, "Please verify your email first."

    return user, None
