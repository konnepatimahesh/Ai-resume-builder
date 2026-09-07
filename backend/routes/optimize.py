from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
from utils.decorators import login_required_api
from services.resume_parser import parse_resume
from services.ai_optimizer import optimize_resume
from models.resume_history import ResumeHistory
from database import db
import os

optimize_bp = Blueprint("optimize", __name__)

@optimize_bp.route("/optimize", methods=["POST"])
@login_required_api
def optimize():
    data        = request.get_json(silent=True) or {}
    filename    = data.get("filename", "")
    job_desc    = data.get("job_desc", "")
    missing     = data.get("missing_skills", [])
    history_id  = data.get("history_id")

    if not filename or not job_desc:
        return jsonify({"error": "filename and job_desc are required."}), 400

    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Original file not found."}), 404

    if history_id:
        h = ResumeHistory.query.filter_by(id=history_id, user_id=current_user.id).first()
        if h and h.optimised_file_path:
            opt_path = os.path.join(current_app.config["OUTPUT_FOLDER"], h.optimised_file_path)
            if os.path.exists(opt_path):
                try:
                    with open(opt_path, "r", encoding="utf-8") as f:
                        optimized_text = f.read()
                    return jsonify({"optimized_resume": optimized_text}), 200
                except Exception as e:
                    print(f"[CACHE READ ERROR] {e}")

    try:
        parsed = parse_resume(filepath)
        optimized_text = optimize_resume(parsed["raw_text"], job_desc, missing)
    except Exception as e:
        return jsonify({"error": f"Optimization failed: {str(e)}"}), 500

    if history_id:
        h = ResumeHistory.query.filter_by(id=history_id, user_id=current_user.id).first()
        if h:
            import uuid
            opt_filename = f"resume_opt_{uuid.uuid4().hex}.txt"
            opt_path = os.path.join(current_app.config["OUTPUT_FOLDER"], opt_filename)
            try:
                with open(opt_path, "w", encoding="utf-8") as f:
                    f.write(optimized_text)
                h.optimised_file_path = opt_filename
                db.session.commit()
            except Exception as e:
                print(f"[CACHE WRITE ERROR] {e}")

    return jsonify({"optimized_resume": optimized_text}), 200
