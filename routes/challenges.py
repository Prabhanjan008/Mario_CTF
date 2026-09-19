from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from models.team import (
    get_or_create_default_team,
    get_team_by_id,
    start_team_timer,
    finish_team_timer,
    update_team_last_challenge
)
from models.challenge import (
    get_worlds_with_status,
    get_challenges_by_world,
    get_challenge_detail,
    verify_and_solve_flag,
    unlock_hint
)

challenges_bp = Blueprint("challenges", __name__)

def get_current_team():
    team_id = session.get("team_id")
    if team_id:
        team = get_team_by_id(team_id)
        if team:
            return team
    default_team = get_or_create_default_team()
    session["team_id"] = default_team["id"]
    return default_team

@challenges_bp.route("/challenge/<int:challenge_id>")
def view_challenge(challenge_id: int):
    team = get_current_team()
    challenge = get_challenge_detail(challenge_id, team["id"])
    if not challenge:
        return redirect(url_for("game.world_map"))

    # Check if world is unlocked
    worlds = get_worlds_with_status(team["id"])
    world_dict = {w["id"]: w for w in worlds}
    world_info = world_dict.get(challenge["world_id"])
    if not world_info or not world_info["is_unlocked"]:
        return render_template("locked.html", team=team, world=world_info, required=world_info["required_stars"] if world_info else 0)

    # Officially start competition timer when player enters challenge!
    if team.get("started_at") is None:
        start_team_timer(team["id"])
        team = get_team_by_id(team["id"])

    # Record active position so players can resume where they stopped
    update_team_last_challenge(team["id"], challenge_id)
    session["last_challenge_id"] = challenge_id

    # If it's Challenge 12 (Boss challenge), render boss interface
    if challenge["slug"] == "w5-c1" or challenge["interactive_type"] == "boss_terminal":
        return render_template("boss.html", team=team, challenge=challenge)

    return render_template("challenge.html", team=team, challenge=challenge)

@challenges_bp.route("/boss")
def view_boss():
    return redirect(url_for("challenges.view_challenge", challenge_id=12))

@challenges_bp.route("/api/submit-flag", methods=["POST"])
def submit_flag():
    team = get_current_team()
    data = request.get_json() or {}
    challenge_id = data.get("challenge_id")
    flag = data.get("flag", "").strip()

    if not challenge_id or not flag:
        return jsonify({"success": False, "message": "Challenge ID and Flag are required"}), 400

    result = verify_and_solve_flag(team["id"], int(challenge_id), flag)
    # Refresh updated team info
    updated_team = get_team_by_id(team["id"])

    if result.get("success"):
        c_id = int(challenge_id)
        if c_id < 12:
            next_id = c_id + 1
            update_team_last_challenge(team["id"], next_id)
            session["last_challenge_id"] = next_id
        else:
            update_team_last_challenge(team["id"], 12)
            session["last_challenge_id"] = 12

    # If completed boss or reached 12 stars, officially stop/freeze the CTF timer!
    if result.get("success") and (int(challenge_id) == 12 or updated_team["stars"] >= 12):
        finish_team_timer(team["id"])
        updated_team = get_team_by_id(team["id"])

    result["team"] = {
        "score": updated_team["score"],
        "coins": updated_team["coins"],
        "stars": updated_team["stars"],
        "current_world": updated_team["current_world"],
        "started_at": updated_team.get("started_at"),
        "finished_at": updated_team.get("finished_at"),
        "total_time": updated_team.get("total_time")
    }
    return jsonify(result)

@challenges_bp.route("/api/unlock-hint", methods=["POST"])
def api_unlock_hint():
    team = get_current_team()
    data = request.get_json() or {}
    challenge_id = data.get("challenge_id")
    hint_num = data.get("hint_num")

    if not challenge_id or not hint_num:
        return jsonify({"success": False, "message": "Invalid request"}), 400

    result = unlock_hint(team["id"], int(challenge_id), int(hint_num))
    updated_team = get_team_by_id(team["id"])
    result["remaining_coins"] = updated_team["coins"]
    return jsonify(result)

@challenges_bp.route("/api/world/<int:world_id>/challenges")
def api_world_challenges(world_id: int):
    team = get_current_team()
    challenges = get_challenges_by_world(world_id, team["id"])
    return jsonify(challenges)
