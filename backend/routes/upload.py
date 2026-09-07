from flask import Blueprint, request, jsonify
from flask_login import current_user
from utils.decorators import login_required_api
from utils.file_handler import save_upload
from database import db
from models.resume_history import ResumeHistory, SearchLog

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/upload", methods=["POST"])
@login_required_api
def upload():
    if "resume" not in request.files:
        return jsonify({"error": "No file provided."}), 400

    file      = request.files["resume"]
    job_title = request.form.get("job_title", "").strip()
    job_desc  = request.form.get("job_desc", "").strip()

    try:
        path, filename = save_upload(file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    history = ResumeHistory(
        user_id=current_user.id,
        job_title=job_title or "Untitled",
        job_desc=job_desc,
        uploaded_file_path=filename,
    )
    db.session.add(history)
    log = SearchLog(user_id=current_user.id, query_text=f"Upload: {filename} | Job: {job_title}")
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "message":    "File uploaded successfully.",
        "filename":   filename,
        "history_id": history.id,
        "job_desc":   job_desc,
    }), 200
