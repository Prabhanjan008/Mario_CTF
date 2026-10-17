"""
Mario: The Cyber Heist — Production Flask Application Entrypoint.
Configured for 100+ concurrent teams with multi-member squad isolation,
CSRF protection, secure cookie handling, and production WSGI compatibility.
"""

import os
from datetime import timedelta
from flask import Flask, render_template, session, request
from models.db import init_database, db_session
from models.schema import Team
from services.auth_service import get_current_team_and_member, get_or_create_csrf_token
from services.run_service import get_team_run_info, get_team_resume_target
from routes.game import game_bp
from routes.challenges import challenges_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Security & Session Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "mario-ojas-cyber-heist-secret-key-2026")
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = (
        os.environ.get("FLASK_ENV") == "production" or
        os.environ.get("HTTPS") == "1"
    )
    # Request size limits to prevent memory exhaustion / DoS
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    # Ensure Database tables and initial seed data exist
    try:
        init_database(reset=False, seed=True)
    except Exception as e:
        print(f"Notice: Database check during app initialization: {e}")

    @app.before_request
    def setup_session_and_csrf():
        session.permanent = True
        # Ensure CSRF token exists for the session
        get_or_create_csrf_token()

    @app.context_processor
    def inject_globals():
        try:
            from datetime import datetime, timezone
            from services.competition_service import get_competition_status
            comp_status = get_competition_status()
            now_utc = datetime.now(timezone.utc)
            server_time_ms = int(now_utc.timestamp() * 1000)

            with db_session() as sess:
                team, member = get_current_team_and_member(sess)
                team_dict = team.to_dict() if team else None
                member_name = member.member_name if member else None
                run_info = get_team_run_info(team) if team else None

            resume_info = get_team_resume_target(team_dict["id"]) if team_dict else None
            csrf_tok = get_or_create_csrf_token()

            return dict(
                team=team_dict,
                member_name=member_name,
                resume_info=resume_info,
                run_info=run_info,
                competition=comp_status,
                server_time_ms=server_time_ms,
                csrf_token=csrf_tok
            )
        except Exception:
            from datetime import datetime, timezone
            now_utc = datetime.now(timezone.utc)
            return dict(
                team=None,
                member_name=None,
                resume_info=None,
                run_info=None,
                competition={"status": "LOBBY", "can_play": False},
                server_time_ms=int(now_utc.timestamp() * 1000),
                csrf_token=get_or_create_csrf_token()
            )

    # Register Blueprints
    app.register_blueprint(game_bp)
    app.register_blueprint(challenges_bp)
    app.register_blueprint(admin_bp)

    @app.route("/api/health")
    def health_check():
        return {
            "status": "online",
            "game": "Mario: The Cyber Heist",
            "edition": "OJAS 2026 Production Upgrade",
            "database": "connected"
        }

    @app.route("/api/diag")
    def diagnostics():
        results = {}
        import traceback
        try:
            from models.db import db_session, engine, IS_SQLITE
            results["db_type"] = "sqlite" if IS_SQLITE else "postgresql"
            results["engine_url"] = str(engine.url).split("@")[-1]
            with db_session() as sess:
                from models.schema import CompetitionState, Team, Challenge, World
                results["worlds_count"] = sess.query(World).count()
                results["challenges_count"] = sess.query(Challenge).count()
                comp = sess.query(CompetitionState).first()
                results["comp_status"] = comp.status if comp else "MISSING"
                results["teams_count"] = sess.query(Team).count()
                sample_team = sess.query(Team.id, Team.team_name, Team.student_name, Team.register_number).first()
                results["sample_team"] = str(sample_team) if sample_team else "none"
            results["status"] = "ALL_HEALTHY"
        except Exception as ex:
            results["status"] = "ERROR"
            results["error"] = str(ex)
            results["traceback"] = traceback.format_exc()
        return results

    @app.errorhandler(403)
    def forbidden(e):
        return {"error": "Forbidden: Request verification or authorization failed."}, 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        import traceback
        import sys
        print("--- 500 INTERNAL SERVER ERROR ---", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        err_msg = str(getattr(e, "original_exception", e))
        return {
            "error": "Internal Server Error. Forensic incident logged.",
            "detail": err_msg
        }, 500

    return app


app = create_app()

if __name__ == "__main__":
    # Host on 0.0.0.0 for LAN tech fest access
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
