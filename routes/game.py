"""
Game Session, Navigation & Team Controller (Thin Routes).
Delegates all business logic to auth_service, run_service, progression_service, and leaderboard_service.
"""

from datetime import datetime, timezone
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from models.db import db_session
from models.schema import Team, Challenge, SolvedChallenge
from services.auth_service import (
    register_team as svc_register_team,
    join_team_by_code,
    get_current_team_and_member,
    get_client_ip,
    validate_csrf
)
from services.run_service import (
    start_team_run,
    complete_team_run,
    reopen_team_run,
    get_team_run_info,
    get_team_resume_target
)
from services.progression_service import (
    get_worlds_with_status,
    calculate_normal_stars
)
from services.leaderboard_service import get_leaderboard_standings

game_bp = Blueprint("game", __name__)


def get_current_team():
    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        return team.to_dict() if team else None


@game_bp.route("/")
def index():
    from services.competition_service import get_competition_status
    comp = get_competition_status()

    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        team_dict = team.to_dict() if team else None
        resume_info = get_team_resume_target(team.id) if team else None

    # Automatically navigate based on competition state and squad status
    if request.args.get("home") != "1":
        if not team:
            # New visitor: redirect to squad registration
            return redirect(url_for("game.briefing"))
        elif comp["status"] == "LOBBY":
            # Squad registered, awaiting host dispatch
            return redirect(url_for("game.lobby"))
        elif resume_info and resume_info.get("is_started") and not resume_info.get("is_finished"):
            return redirect(resume_info["resume_url"])

    return render_template("index.html", team=team_dict, resume_info=resume_info, comp=comp)


@game_bp.route("/lobby")
def lobby():
    """Mission Standby Room: where students gather until the Host starts the game."""
    from services.competition_service import get_competition_status
    comp = get_competition_status()

    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        if not team:
            return redirect(url_for("game.briefing"))

        # If Host has already started the competition, jump directly to 3D Map
        if comp["status"] == "ACTIVE":
            return redirect(url_for("game.world_map"))

        team_dict = team.to_dict()
        members = [m.member_name for m in team.members]

    return render_template("lobby.html", team=team_dict, members=members, comp=comp)


@game_bp.route("/api/competition/status")
def api_competition_status():
    """Live telemetry polling endpoint for standby lobby and game HUD."""
    from services.competition_service import get_competition_status
    status = get_competition_status()
    now_utc = datetime.now(timezone.utc)
    status["server_time_ms"] = int(now_utc.timestamp() * 1000)

    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        if team:
            run_info = get_team_run_info(team)
            status["team"] = {
                "id": team.id,
                "team_name": team.team_name,
                "access_code": team.access_code,
                "run_state": team.run_state,
                "score": team.score,
                "coins": team.coins,
                "stars": team.stars,
                "members": [m.member_name for m in team.members],
                "run_info": run_info
            }
        else:
            status["team"] = None
    return jsonify(status)


@game_bp.route("/briefing")
def briefing():
    from services.competition_service import get_competition_status
    comp = get_competition_status()

    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        team_dict = team.to_dict() if team else None
        all_teams = [t.to_dict() for t in sess.query(Team).order_by(Team.id.asc()).all()]

    return render_template("briefing.html", team=team_dict, all_teams=all_teams, comp=comp)


@game_bp.route("/map")
def world_map():
    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        if not team:
            return redirect(url_for("game.briefing"))

        from services.competition_service import get_competition_status
        comp = get_competition_status()
        if comp["status"] == "LOBBY":
            return redirect(url_for("game.lobby"))

        team_dict = team.to_dict()
        worlds = get_worlds_with_status(team_dict["id"])

    return render_template("map.html", team=team_dict, worlds=worlds, comp=comp)


@game_bp.route("/victory")
def victory():
    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        if not team:
            return redirect(url_for("game.index"))
        team_dict = team.to_dict()
        run_info = get_team_run_info(team)
        normal_stars = calculate_normal_stars(team.id, sess)

        # Protect victory screen from unauthorized access
        has_boss_solve = (
            sess.query(SolvedChallenge)
            .filter_by(team_id=team.id, challenge_id=12)
            .first() is not None
        )
        if not has_boss_solve and not run_info["is_completed"] and normal_stars < 11:
            return redirect(url_for("game.world_map"))

    return render_template("victory.html", team=team_dict, run_info=run_info)


@game_bp.route("/end")
@game_bp.route("/debrief")
def end_section():
    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        if not team:
            return redirect(url_for("game.index"))
        team_dict = team.to_dict()

        # Audit stream of 12 challenges
        challenges = sess.query(Challenge).order_by(Challenge.id.asc()).all()
        solves_map = {
            s.challenge_id: s.solved_at.isoformat() if s.solved_at else "VERIFIED"
            for s in sess.query(SolvedChallenge).filter_by(team_id=team.id).all()
        }

        challenges_status = []
        for c in challenges:
            c_dict = c.to_dict(mask_hints=True, mask_secrets=True)
            c_dict["world_name"] = c.world.name if c.world else ""
            c_dict["world_icon"] = c.world.icon if c.world else "🍄"
            c_dict["is_solved"] = c.id in solves_map
            c_dict["solved_at"] = solves_map.get(c.id)
            challenges_status.append(c_dict)

        standings = get_leaderboard_standings()
        rank = 1
        for idx, item in enumerate(standings, start=1):
            if item["id"] == team.id:
                rank = idx
                break

    return render_template(
        "end.html",
        team=team_dict,
        challenges_status=challenges_status,
        rank=rank,
        total_teams=len(standings)
    )


@game_bp.route("/leaderboard")
def leaderboard():
    from services.admin_service import is_admin_authenticated
    if not is_admin_authenticated():
        return render_template(
            "admin_login.html",
            error="🔒 Access Restricted: The live leaderboard is reserved for Event Hosts / Organizers only. Please authenticate with the Host Security Key."
        )

    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        team_dict = team.to_dict() if team else None

    board = get_leaderboard_standings()
    return render_template("leaderboard.html", team=team_dict, leaderboard=board)


# ==========================================
# TEAM MANAGEMENT & REGISTRATION APIS
# ==========================================
@game_bp.route("/api/team/register", methods=["POST"])
def api_register_team():
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid or missing CSRF token."}), 403

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or data.get("team_name") or "").strip()
    register_number = (data.get("register_number") or data.get("reg_no") or "").strip()
    phone = (data.get("phone") or data.get("phone_number") or "").strip()
    member_name = (data.get("member_name") or name or "Operative").strip()
    ip = get_client_ip(request)

    res = svc_register_team(
        team_name=name,
        member_name=member_name,
        register_number=register_number,
        phone_number=phone,
        ip=ip
    )
    if not res["success"]:
        return jsonify(res), 400
    return jsonify(res)


@game_bp.route("/api/team/switch", methods=["POST"])
def api_switch_team():
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid or missing CSRF token."}), 403

    data = request.get_json(silent=True) or {}
    access_code = data.get("identifier") or data.get("access_code") or ""
    member_name = data.get("member_name", "Agent").strip()
    ip = get_client_ip(request)

    res = join_team_by_code(str(access_code), member_name=member_name, ip=ip)
    if not res["success"]:
        return jsonify(res), 400

    team_id = res["team"]["id"]
    resume_info = get_team_resume_target(team_id)
    res.update({
        "resume_url": resume_info["resume_url"],
        "resume_label": resume_info["resume_label"],
        "is_started": resume_info["is_started"]
    })
    return jsonify(res)


@game_bp.route("/api/team/set-name", methods=["POST"])
def set_team_name():
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid or missing CSRF token."}), 403

    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        if not team:
            return jsonify({"success": False, "message": "No active squad."}), 400
        team_id = team.id

    data = request.get_json(silent=True) or {}
    new_name = data.get("name", "").strip()
    if not new_name:
        return jsonify({"success": False, "message": "Team name cannot be empty."}), 400

    from models.team import update_team_name
    res = update_team_name(team_id, new_name)
    if not res["success"]:
        return jsonify(res), 400
    return jsonify(res)


# ==========================================
# RUN LIFECYCLE APIS
# ==========================================
@game_bp.route("/api/run/start", methods=["POST"])
def api_start_run():
    """Explicit, state-changing POST endpoint to start the competition clock."""
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid or missing CSRF token."}), 403

    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        if not team:
            return jsonify({"success": False, "message": "No active squad."}), 400
        team_id = team.id

    ip = get_client_ip(request)
    res = start_team_run(team_id, ip=ip)
    return jsonify(res)


@game_bp.route("/api/team/stop-mission", methods=["POST"])
def api_stop_mission():
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid or missing CSRF token."}), 403

    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        if not team:
            return jsonify({"success": False, "message": "No active squad."}), 400
        ip = get_client_ip(request)
        run_info = complete_team_run(team, sess=sess, ip=ip)

    return jsonify({
        "success": True,
        "message": f"Mission concluded! Competition clock locked at {run_info['formatted_time']}.",
        "run_info": run_info,
        "redirect_url": "/end"
    })


@game_bp.route("/api/team/reopen-mission", methods=["POST"])
def api_reopen_mission():
    if not validate_csrf(request):
        return jsonify({"success": False, "message": "Invalid or missing CSRF token."}), 403

    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        if not team:
            return jsonify({"success": False, "message": "No active squad."}), 400
        team_id = team.id

    ip = get_client_ip(request)
    res = reopen_team_run(team_id, admin_ip=ip)
    resume = get_team_resume_target(team_id)
    return jsonify({
        "success": True,
        "message": "Mission resumed! Competition clock reopened.",
        "run_info": res.get("run_info"),
        "redirect_url": resume["resume_url"]
    })


@game_bp.route("/api/team/status")
def team_status():
    with db_session() as sess:
        team, member = get_current_team_and_member(sess)
        run_info = get_team_run_info(team)
        normal_stars = calculate_normal_stars(team.id, sess)

        return jsonify({
            "id": team.id,
            "name": team.team_name,
            "member_name": member.member_name if member else "Agent",
            "score": team.score,
            "coins": team.coins,
            "stars": normal_stars,
            "current_world": team.current_world,
            "run_info": run_info
        })


@game_bp.route("/api/teams", methods=["GET"])
def api_list_teams():
    with db_session() as sess:
        teams = [
            {
                "id": t.id,
                "team_name": t.team_name,
                "score": t.score,
                "stars": t.stars,
                "coins": t.coins,
                "current_world": t.current_world
            }
            for t in sess.query(Team).order_by(Team.score.desc(), Team.stars.desc()).all()
        ]
    return jsonify(teams)
