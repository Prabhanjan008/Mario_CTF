import os
from datetime import timedelta
from flask import Flask, render_template, session
from routes.game import game_bp, get_current_team
from routes.challenges import challenges_bp
from routes.admin import admin_bp
from database.init_db import init_db, DB_PATH
from models.team import get_team_resume_target

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "mario-ojas-cyber-heist-secret-key-2026")
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
    
    # Ensure DB is created if missing
    if not os.path.exists(DB_PATH):
        init_db(reset=False)

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    @app.context_processor
    def inject_globals():
        try:
            team = get_current_team()
            resume_info = get_team_resume_target(team["id"]) if team else None
            return dict(team=team, resume_info=resume_info)
        except Exception:
            return dict(team=None, resume_info=None)

    # Register blueprints
    app.register_blueprint(game_bp)
    app.register_blueprint(challenges_bp)
    app.register_blueprint(admin_bp)

    @app.route("/api/health")
    def health_check():
        return {"status": "online", "game": "Mario: The Cyber Heist", "edition": "OJAS 2026"}

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    return app

app = create_app()

if __name__ == "__main__":
    # Host on 0.0.0.0 for LAN tech fest access
    app.run(host="0.0.0.0", port=5000, debug=True)
