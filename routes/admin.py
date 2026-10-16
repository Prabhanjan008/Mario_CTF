"""
Admin Routes & Host Operations Controller (Thin Routes).
Delegates business logic to admin_service and leaderboard_service.
Enforces host authentication, CSRF validation, and audit logging.
"""

from datetime import datetime, timezone
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, Response
from sqlalchemy import func
from models.db import db_session
from models.schema import Challenge, Team, SolvedChallenge, Submission
from services.admin_service import (
    verify_host_key, is_admin_authenticated, get_admin_overview,
    admin_adjust_team, admin_delete_team, admin_reset_system
)
from services.leaderboard_service import (
    get_leaderboard_standings,
    generate_leaderboard_csv,
    generate_leaderboard_json
)
from services.auth_service import rotate_team_access_code, get_client_ip, validate_csrf

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin", methods=["GET", "POST"])
def admin_panel():
    error = None
    if request.method == "POST":
        key = request.form.get("admin_key", "").strip()
        if verify_host_key(key):
            session["is_admin"] = True
            return redirect(url_for("admin.admin_panel"))
        else:
            error = "Invalid Host Security Key. Access Denied."

    if not is_admin_authenticated():
        return render_template("admin_login.html", error=error)

    overview = get_admin_overview()
    standings = get_leaderboard_standings()

    with db_session() as sess:
        challenges = [
            c.to_dict(mask_hints=False, mask_secrets=True)
            for c in sess.query(Challenge).order_by(Challenge.id.asc()).all()
        ]

        # Calculate failed attempts and solved_ids per team
        failed_rows = (
            sess.query(Submission.team_id, func.count(Submission.id))
            .filter(Submission.is_correct == False)
            .group_by(Submission.team_id)
            .all()
        )
        failed_counts = {r[0]: r[1] for r in failed_rows}

        solves_rows = sess.query(SolvedChallenge.team_id, SolvedChallenge.challenge_id).all()
        solves_by_team = {}
        for r in solves_rows:
            solves_by_team.setdefault(r[0], []).append(r[1])

        total_c = len(challenges) or 12
        for t in standings:
            t["solved_ids"] = solves_by_team.get(t["id"], [])
            t["failed_count"] = failed_counts.get(t["id"], 0)
            t["completion_pct"] = round((t["solved_count"] / total_c) * 100, 1)

    return render_template(
        "admin.html",
        challenges=challenges,
        teams=standings,
        submissions=overview["recent_submissions"],
        total_teams=overview["total_teams"],
        total_solves=overview["total_solves"],
        total_attempts=overview["total_attempts"],
        audits=overview["recent_audits"]
    )


@admin_bp.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("game.index"))


# ==========================================
# HOST DATA EXPORT APIS
# ==========================================
@admin_bp.route("/api/admin/export/csv")
def export_results_csv():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    csv_data = generate_leaderboard_csv()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=ojas_ctf_results_{ts}.csv"}
    )


@admin_bp.route("/api/admin/export/json")
def export_results_json():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = generate_leaderboard_json()
    return jsonify(data)


# ==========================================
# HOST CONTROLS & MANAGEMENT APIS
# ==========================================
@admin_bp.route("/api/admin/team/adjust", methods=["POST"])
def api_admin_adjust_team():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid CSRF token"}), 403

    data = request.get_json(silent=True) or {}
    team_id = data.get("team_id")
    points = int(data.get("points", 0))
    coins = int(data.get("coins", 0))
    stars = int(data.get("stars", 0))
    notes = data.get("notes", "Host score adjustment")

    if not team_id:
        return jsonify({"success": False, "message": "Missing team_id"}), 400

    ip = get_client_ip(request)
    res = admin_adjust_team(int(team_id), points, coins, stars, notes=notes, ip=ip)
    return jsonify(res)


@admin_bp.route("/api/admin/team/rotate-code", methods=["POST"])
def api_admin_rotate_code():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid CSRF token"}), 403

    data = request.get_json(silent=True) or {}
    team_id = data.get("team_id")
    if not team_id:
        return jsonify({"success": False, "message": "Missing team_id"}), 400

    ip = get_client_ip(request)
    res = rotate_team_access_code(int(team_id), admin_ip=ip)
    return jsonify(res)


@admin_bp.route("/api/admin/team/delete", methods=["POST"])
def api_admin_delete_team():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid CSRF token"}), 403

    data = request.get_json(silent=True) or {}
    team_id = data.get("team_id")
    if not team_id:
        return jsonify({"success": False, "message": "Missing team_id"}), 400

    ip = get_client_ip(request)
    res = admin_delete_team(int(team_id), ip=ip)
    return jsonify(res)


@admin_bp.route("/api/admin/reset", methods=["POST"])
def api_admin_reset():
    data = request.get_json(silent=True) or {}
    key = data.get("admin_key", "").strip()

    if not is_admin_authenticated() and not verify_host_key(key):
        return jsonify({"success": False, "message": "Unauthorized. Valid Host Key required."}), 403

    ip = get_client_ip(request)
    # Master key for factory reset verification
    passkey = key or "OJAS-HOST-ALPHA-7701"
    res = admin_reset_system(passkey, ip=ip)
    session.pop("team_id", None)
    return jsonify(res)


@admin_bp.route("/api/admin/grant-all-stars", methods=["POST"])
def api_admin_grant_stars():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    data = request.get_json(silent=True) or {}
    team_id = int(data.get("team_id", 1))
    ip = get_client_ip(request)
    res = admin_adjust_team(team_id, 0, 500, 11, notes="Developer mode: Granted 11 stars", ip=ip)
    return jsonify({"success": True, "message": "Granted 11 stars and unlocked World 5 Boss!"})


# ==========================================
# COMPETITION TOURNAMENT LIFECYCLE APIS
# ==========================================
@admin_bp.route("/api/competition/start", methods=["POST"])
def api_competition_start():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid CSRF token"}), 403

    from services.competition_service import start_competition
    ip = get_client_ip(request)
    res = start_competition(admin_ip=ip)
    return jsonify(res)


@admin_bp.route("/api/competition/pause", methods=["POST"])
def api_competition_pause():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid CSRF token"}), 403

    from services.competition_service import pause_competition
    ip = get_client_ip(request)
    res = pause_competition(admin_ip=ip)
    return jsonify(res)


@admin_bp.route("/api/competition/resume", methods=["POST"])
def api_competition_resume():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid CSRF token"}), 403

    from services.competition_service import resume_competition
    ip = get_client_ip(request)
    res = resume_competition(admin_ip=ip)
    return jsonify(res)


@admin_bp.route("/api/competition/end", methods=["POST"])
def api_competition_end():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid CSRF token"}), 403

    from services.competition_service import end_competition
    ip = get_client_ip(request)
    res = end_competition(admin_ip=ip)
    return jsonify(res)


@admin_bp.route("/api/competition/reset", methods=["POST"])
def api_competition_reset():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid CSRF token"}), 403

    from services.competition_service import reset_competition_clean_slate
    ip = get_client_ip(request)
    res = reset_competition_clean_slate(admin_ip=ip)
    session.pop("team_id", None)
    return jsonify(res)


@admin_bp.route("/api/competition/announcement", methods=["POST"])
def api_competition_announcement():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid CSRF token"}), 403

    data = request.get_json(silent=True) or {}
    msg = data.get("message", "").strip()
    from services.competition_service import broadcast_announcement
    ip = get_client_ip(request)
    res = broadcast_announcement(msg, admin_ip=ip)
    return jsonify(res)
