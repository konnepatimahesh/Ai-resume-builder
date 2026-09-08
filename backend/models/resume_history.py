
from database import db
from datetime import datetime


class EmailToken(db.Model):
    __tablename__ = "email_tokens"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    token = db.Column(
        db.String(256),
        unique=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=False
    )


class ResumeHistory(db.Model):
    __tablename__ = "resume_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    job_title = db.Column(
        db.String(200)
    )

    job_desc = db.Column(
        db.Text
    )

    ats_score = db.Column(
        db.Float
    )

    keyword_score = db.Column(
        db.Float
    )

    skill_score = db.Column(
        db.Float
    )

    structure_score = db.Column(
        db.Float
    )

    matched_skills = db.Column(
        db.Text
    )

    missing_skills = db.Column(
        db.Text
    )

    recommendations = db.Column(
        db.Text
    )

    uploaded_file_path = db.Column(
        db.String(400)
    )

    optimised_file_path = db.Column(
        db.String(400)
    )

    pdf_path = db.Column(
        db.String(400)
    )

    docx_path = db.Column(
        db.String(400)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        import json

        return {
            "id": self.id,
            "job_title": self.job_title,
            "job_desc": self.job_desc,
            "ats_score": self.ats_score,
            "keyword_score": self.keyword_score,
            "skill_score": self.skill_score,
            "structure_score": self.structure_score,
            "matched_skills": (
                json.loads(self.matched_skills)
                if self.matched_skills
                else []
            ),
            "missing_skills": (
                json.loads(self.missing_skills)
                if self.missing_skills
                else []
            ),
            "recommendations": (
                json.loads(self.recommendations)
                if self.recommendations
                else []
            ),
            "uploaded_file_path": self.uploaded_file_path,
            "optimised_file_path": self.optimised_file_path,
            "pdf_path": self.pdf_path,
            "docx_path": self.docx_path,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }


class SearchLog(db.Model):
    __tablename__ = "search_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    query_text = db.Column(
        db.Text
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "query_text": self.query_text,
            "timestamp": (
                self.timestamp.isoformat()
                if self.timestamp
                else None
            ),
        }