from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from services.auth_service import register_user, authenticate, verify_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not name or not email or not password:
        return jsonify({
            "error": "All fields are required."
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters."
        }), 400

    user, err = register_user(
        name,
        email,
        password
    )

    if err:
        if err == "Email already registered.":
            return jsonify({
                "error": err
            }), 409

        return jsonify({
            "error": err
        }), 503

    return jsonify({
        "message": "Registration successful. Check your email to verify your account."
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email    = (data.get("email")    or "").strip()
    password = (data.get("password") or "").strip()

    user, err = authenticate(email, password)
    if err:
        return jsonify({"error": err}), 401

    login_user(user, remember=True)
    return jsonify({"message": "Login successful.", "user": user.to_dict()}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return jsonify({"message": "Logged out."}), 200


@auth_bp.route("/verify/<token>", methods=["GET"])
def verify(token):
    user, err = verify_token(token)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"message": "Email verified successfully. You can now log in."}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authenticated."}), 401
    return jsonify({"user": current_user.to_dict()}), 200