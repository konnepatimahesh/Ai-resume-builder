from flask import Blueprint, jsonify
from flask_login import current_user
from utils.decorators import login_required_api
from models.resume_history import ResumeHistory

history_bp = Blueprint("history", __name__)


@history_bp.route("/history", methods=["GET"])
@login_required_api
def history():
    rows = ResumeHistory.query.filter_by(user_id=current_user.id)\
               .order_by(ResumeHistory.created_at.desc()).all()
    return jsonify({"history": [r.to_dict() for r in rows]}), 200


@history_bp.route("/history/<int:history_id>", methods=["GET"])
@login_required_api
def get_history_item(history_id):
    h = ResumeHistory.query.filter_by(id=history_id, user_id=current_user.id).first()
    if not h:
        return jsonify({"error": "History item not found."}), 404
    return jsonify({"history": h.to_dict()}), 200