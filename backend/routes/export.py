
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import current_user
from utils.decorators import login_required_api
from services.pdf_generator import generate_pdf
from services.docx_generator import generate_docx
from services.email_resume_service import send_resume_email
from models.resume_history import ResumeHistory
from database import db
import os, uuid

export_bp   = Blueprint("export", __name__)
download_bp = Blueprint("download", __name__)


@export_bp.route("/export", methods=["POST"])
@login_required_api
def export():
    data       = request.get_json(silent=True) or {}
    text       = data.get("optimized_resume", "")
    file_type  = data.get("type", "pdf")
    history_id = data.get("history_id")

    if not text:
        return jsonify({"error": "No resume content provided."}), 400

    uid = uuid.uuid4().hex
    output_dir = current_app.config["OUTPUT_FOLDER"]

    if file_type == "docx":
        filename = f"resume_{uid}.docx"
        path = os.path.join(output_dir, filename)
        generate_docx(text, path)
    else:
        filename = f"resume_{uid}.pdf"
        path = os.path.join(output_dir, filename)
        generate_pdf(text, path)

    if history_id:
        h = ResumeHistory.query.filter_by(id=history_id, user_id=current_user.id).first()
        if h:
            if file_type == "docx":
                h.docx_path = filename
            else:
                h.pdf_path = filename
            db.session.commit()

    return jsonify({"filename": filename, "url": f"/outputs/{filename}"}), 200


@export_bp.route("/email-resume", methods=["POST"])
@login_required_api
def email_resume():
    data           = request.get_json(silent=True) or {}
    text           = data.get("optimized_resume", "")
    history_id     = data.get("history_id")
    job_title      = data.get("job_title", "Job Position")
    ats_score      = data.get("ats_score", 0)
    matched_skills = data.get("matched_skills", [])
    missing_skills = data.get("missing_skills", [])

    if not text:
        return jsonify({"error": "No resume content provided."}), 400

    output_dir = current_app.config["OUTPUT_FOLDER"]
    uid = uuid.uuid4().hex
    filename = f"resume_{uid}.pdf"
    path = os.path.join(output_dir, filename)

    try:
        generate_pdf(text, path)
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500

    if history_id:
        h = ResumeHistory.query.filter_by(id=history_id, user_id=current_user.id).first()
        if h:
            h.pdf_path = filename
            db.session.commit()

    try:
        send_resume_email(
            user=current_user,
            pdf_path=path,
            ats_score=float(ats_score),
            job_title=job_title,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
        )
    except Exception as e:
        print(f"[EMAIL RESUME ERROR] {type(e).__name__}: {e}")
        return jsonify({"error": f"Could not send email: {str(e)}"}), 500

    return jsonify({"message": f"Resume emailed to {current_user.email} successfully!"}), 200


@download_bp.route("/outputs/<filename>", methods=["GET"])
@login_required_api
def download_output(filename):
    return send_from_directory(current_app.config["OUTPUT_FOLDER"], filename, as_attachment=True)
