"""
Challenge Presentation & Flag Verification Controller (Thin Routes).
Delegates to progression_service, challenge_service, and boss_service.
Includes server-side APIs for the 3-stage Boss Showdown.
"""

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from models.db import db_session
from models.schema import Team
from services.auth_service import get_current_team_and_member, get_client_ip, validate_csrf
from services.progression_service import (
    is_challenge_unlocked,
    get_challenge_detail,
    get_challenges_by_world,
    get_worlds_with_status,
    calculate_normal_stars,
    BOSS_REQUIRED_STARS
)
from services.challenge_service import verify_and_solve_flag, unlock_hint
from services.run_service import start_team_run, get_team_run_info
from services.boss_service import (
    get_boss_status,
    submit_stage1_shield,
    submit_stage2_trivia,
    submit_stage3_final_flag
)

challenges_bp = Blueprint("challenges", __name__)


def get_current_team_id() -> int:
    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        return team.id if team else None


@challenges_bp.route("/challenge/<int:challenge_id>")
def view_challenge(challenge_id: int):
    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        if not team:
            return redirect(url_for("game.briefing"))

        from services.competition_service import get_competition_status
        comp = get_competition_status()
        if comp["status"] == "LOBBY":
            return redirect(url_for("game.lobby"))

        team_id = team.id
        team_dict = team.to_dict()

        # Update last viewed challenge
        team.last_challenge_id = challenge_id
        session["last_challenge_id"] = challenge_id

    # Check unlock status
    unlocked, reason, req_stars = is_challenge_unlocked(team_id, challenge_id)
    if not unlocked:
        worlds = get_worlds_with_status(team_id)
        w_info = next((w for w in worlds if w["id"] == (5 if challenge_id == 12 else 1)), None)
        return render_template("locked.html", team=team_dict, world=w_info, required=req_stars, reason=reason)

    # Render Challenge 12 via 3-Stage Boss Arena
    if challenge_id == 12:
        boss_data = get_boss_status(team_id)
        challenge = get_challenge_detail(challenge_id, team_id)
        return render_template("boss.html", team=team_dict, challenge=challenge, boss_data=boss_data)

    challenge = get_challenge_detail(challenge_id, team_id)
    if not challenge:
        return redirect(url_for("game.world_map"))

    return render_template("challenge.html", team=team_dict, challenge=challenge)


@challenges_bp.route("/boss")
def view_boss():
    return redirect(url_for("challenges.view_challenge", challenge_id=12))


# ==========================================
# FLAG SUBMISSION & HINT APIS
# ==========================================
@challenges_bp.route("/api/submit-flag", methods=["POST"])
def api_submit_flag():
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid or missing CSRF security token."}), 403

    from services.competition_service import get_competition_status
    comp = get_competition_status()
    if comp["status"] != "ACTIVE":
        return jsonify({"success": False, "message": "Competition is currently not active. Stand by for Host launch!"}), 403

    team_id = get_current_team_id()
    if not team_id:
        return jsonify({"success": False, "message": "Squad session missing. Please register or join your squad."}), 401

    data = request.get_json(silent=True) or {}
    challenge_id = data.get("challenge_id")
    flag = data.get("flag", "").strip()

    if not challenge_id or not flag:
        return jsonify({"success": False, "message": "Challenge ID and Flag are required."}), 400

    ip = get_client_ip(request)

    # If submitting Case 12 directly, route through Boss Stage 3 validation
    if int(challenge_id) == 12:
        res = submit_stage3_final_flag(team_id, flag, ip=ip)
        return jsonify(res)

    res = verify_and_solve_flag(team_id, int(challenge_id), flag, ip=ip)
    return jsonify(res)


@challenges_bp.route("/api/unlock-hint", methods=["POST"])
def api_unlock_hint():
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid or missing CSRF security token."}), 403

    team_id = get_current_team_id()
    data = request.get_json(silent=True) or {}
    challenge_id = data.get("challenge_id")
    hint_num = data.get("hint_num")

    if not challenge_id or not hint_num:
        return jsonify({"success": False, "message": "Invalid hint request."}), 400

    ip = get_client_ip(request)
    res = unlock_hint(team_id, int(challenge_id), int(hint_num), ip=ip)
    return jsonify(res)


# ==========================================
# THREE-STAGE BOSS APIS (CASE 12)
# ==========================================
@challenges_bp.route("/api/boss/status")
def api_boss_status():
    team_id = get_current_team_id()
    res = get_boss_status(team_id)
    return jsonify(res)


@challenges_bp.route("/api/boss/override-shield", methods=["POST"])
def api_boss_override_shield():
    """Stage 1: Sector Keycode Override."""
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid or missing CSRF token."}), 403

    team_id = get_current_team_id()
    data = request.get_json(silent=True) or {}
    shield_num = int(data.get("shield_num", 0))
    keycode = str(data.get("keycode", "")).strip()
    ip = get_client_ip(request)

    res = submit_stage1_shield(team_id, shield_num, keycode, ip=ip)
    return jsonify(res)


@challenges_bp.route("/api/boss/submit-trivia", methods=["POST"])
def api_boss_submit_trivia():
    """Stage 2: Cybersecurity Core Knowledge Check."""
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid or missing CSRF token."}), 403

    team_id = get_current_team_id()
    data = request.get_json(silent=True) or {}
    q_num = int(data.get("q_num", 0))
    answer = str(data.get("answer", "")).strip()
    ip = get_client_ip(request)

    res = submit_stage2_trivia(team_id, q_num, answer, ip=ip)
    return jsonify(res)


@challenges_bp.route("/api/boss/submit-final-flag", methods=["POST"])
def api_boss_submit_final_flag():
    """Stage 3: Core Flag Extraction."""
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid or missing CSRF token."}), 403

    team_id = get_current_team_id()
    data = request.get_json(silent=True) or {}
    flag = str(data.get("flag", "")).strip()
    ip = get_client_ip(request)

    res = submit_stage3_final_flag(team_id, flag, ip=ip)
    return jsonify(res)


@challenges_bp.route("/api/world/<int:world_id>/challenges")
def api_world_challenges(world_id: int):
    team_id = get_current_team_id()
    challenges = get_challenges_by_world(world_id, team_id)
    return jsonify(challenges)
