from flask import Blueprint, request, jsonify, current_app
from utils.decorators import login_required_api
from services.resume_parser import parse_resume
import os

parse_bp = Blueprint("parse", __name__)

@parse_bp.route("/parse", methods=["POST"])
@login_required_api
def parse():
    data = request.get_json(silent=True) or {}
    filename = data.get("filename", "")
    if not filename:
        return jsonify({"error": "filename is required."}), 400
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found."}), 404
    try:
        parsed = parse_resume(filepath)
        return jsonify({"parsed": parsed}), 200
    except Exception as e:
        return jsonify({"error": f"Parsing failed: {str(e)}"}), 500