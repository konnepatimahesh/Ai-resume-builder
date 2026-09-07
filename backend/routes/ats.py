from flask import Blueprint, request, jsonify
from flask_login import current_user
from utils.decorators import login_required_api
from services.ats_engine import analyze
from models.resume_history import ResumeHistory
from database import db
import os

ats_bp = Blueprint("ats", __name__)

@ats_bp.route("/ats", methods=["POST"])
@login_required_api
def ats():
    data       = request.get_json(silent=True) or {}
    filename   = data.get("filename", "")
    job_desc   = data.get("job_desc", "")
    history_id = data.get("history_id")

    if not filename or not job_desc:
        return jsonify({"error": "filename and job_desc are required."}), 400

    from flask import current_app
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found. Please upload again."}), 404

    try:
        result = analyze(filepath, job_desc)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

    # Save score and details to history
    if history_id:
        import json
        h = ResumeHistory.query.filter_by(id=history_id, user_id=current_user.id).first()
        if h:
            h.ats_score = result["ats_score"]
            h.keyword_score = result["keyword_score"]
            h.skill_score = result["skill_score"]
            h.structure_score = result["structure_score"]
            h.matched_skills = json.dumps(result["matched_skills"])
            h.missing_skills = json.dumps(result["missing_skills"])
            h.recommendations = json.dumps(result["recommendations"])
            db.session.commit()

    return jsonify(result), 200
