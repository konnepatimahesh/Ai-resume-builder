import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from database import db, login_manager, mail

FRONTEND_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'frontend')

def create_app():
    app = Flask(__name__, static_folder=FRONTEND_FOLDER, static_url_path='')
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = "auth.login"

    CORS(
    app,
    supports_credentials=True,
    origins=[
    	"http://localhost:5500",
    	"http://127.0.0.1:5500",
    	"https://ai-resume-builder-backend-i337.onrender.com",
    	"https://ai-resume-builder-frontend-sarl.onrender.com"
    ]
)

    from routes.auth import auth_bp
    from routes.upload import upload_bp
    from routes.parse import parse_bp
    from routes.ats import ats_bp
    from routes.optimize import optimize_bp
    from routes.export import export_bp, download_bp
    from routes.chat import chat_bp
    from routes.history import history_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp,     url_prefix="/api/auth")
    app.register_blueprint(upload_bp,   url_prefix="/api")
    app.register_blueprint(parse_bp,    url_prefix="/api")
    app.register_blueprint(ats_bp,      url_prefix="/api")
    app.register_blueprint(optimize_bp, url_prefix="/api")
    app.register_blueprint(export_bp,   url_prefix="/api")
    app.register_blueprint(download_bp, url_prefix="")
    app.register_blueprint(chat_bp,     url_prefix="/api")
    app.register_blueprint(history_bp,  url_prefix="/api")
    app.register_blueprint(admin_bp,    url_prefix="/api/admin")

    # ── Serve frontend HTML pages ──────────────────────────────────
    @app.route('/')
    def index():
        return send_from_directory(FRONTEND_FOLDER, 'index.html')

    @app.route('/<path:filename>')
    def frontend(filename):
        # If it's an API call let blueprints handle it
        if filename.startswith('api/'):
            return {'error': 'Not found'}, 404
        try:
            return send_from_directory(FRONTEND_FOLDER, filename)
        except Exception:
            return send_from_directory(FRONTEND_FOLDER, 'index.html')

    with app.app_context():
        db.create_all()
        _seed_admin(app)

    return app

def _seed_admin(app):
    from models.user import User
    admin_email = app.config["ADMIN_EMAIL"]
    if not User.query.filter_by(email=admin_email).first():
        u = User(name="Admin", email=admin_email, role="admin", is_verified=True)
        u.set_password("Admin@1234")
        db.session.add(u)
        db.session.commit()
        print(f"[SEED] Admin created: {admin_email} / Admin@1234  — change this password!")

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)