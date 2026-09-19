from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from models.db import db_session
from models.team import (
    get_or_create_default_team,
    get_team_by_id,
    get_leaderboard,
    register_team,
    update_team_name,
    get_team_by_code,
    get_team_resume_target
)
from models.challenge import get_worlds_with_status

game_bp = Blueprint("game", __name__)

def get_current_team():
    team_id = session.get("team_id")
    if team_id:
        team = get_team_by_id(team_id)
        if team:
            return team
    # Fallback to default team
    default_team = get_or_create_default_team()
    session["team_id"] = default_team["id"]
    return default_team

@game_bp.route("/")
def index():
    team = get_current_team()
    resume_info = get_team_resume_target(team["id"])

    # If the squad has already entered and started the mission,
    # and they didn't explicitly request the title screen via ?home=1,
    # automatically resume where they stopped!
    if request.args.get("home") != "1":
        if resume_info.get("is_started"):
            return redirect(resume_info["resume_url"])

    return render_template("index.html", team=team, resume_info=resume_info)

@game_bp.route("/briefing")
def briefing():
    team = get_current_team()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, team_name, access_code, score, stars, coins, current_world FROM teams ORDER BY id ASC")
        all_teams = [dict(r) for r in cursor.fetchall()]
    return render_template("briefing.html", team=team, all_teams=all_teams)

@game_bp.route("/map")
def world_map():
    team = get_current_team()
    worlds = get_worlds_with_status(team["id"])
    return render_template("map.html", team=team, worlds=worlds)

@game_bp.route("/victory")
def victory():
    team = get_current_team()
    return render_template("victory.html", team=team)

@game_bp.route("/leaderboard")
def leaderboard():
    team = get_current_team()
    board = get_leaderboard()
    return render_template("leaderboard.html", team=team, leaderboard=board)

@game_bp.route("/api/team/set-name", methods=["POST"])
def set_team_name():
    team = get_current_team()
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"success": False, "message": "Team name cannot be empty"}), 400
    
    res = update_team_name(team["id"], name)
    if not res["success"]:
        return jsonify(res), 400
    return jsonify(res)

@game_bp.route("/api/team/register", methods=["POST"])
def api_register_team():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"success": False, "message": "Team name cannot be empty"}), 400
    
    # Check if team already exists
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM teams WHERE LOWER(team_name) = ?", (name.lower(),))
        if cursor.fetchone():
            return jsonify({"success": False, "message": f"Team name '{name}' is already taken. Please choose another name or switch to this squad."}), 400

    new_team = register_team(name)
    session["team_id"] = new_team["id"]
    return jsonify({
        "success": True,
        "message": f"Squad '{new_team['team_name']}' created successfully! Access Code: {new_team['access_code']}",
        "team": new_team
    })

@game_bp.route("/api/team/switch", methods=["POST"])
def api_switch_team():
    data = request.get_json() or {}
    identifier = str(data.get("identifier", "")).strip()
    if not identifier:
        return jsonify({"success": False, "message": "Please enter a team name, access code, or select a squad."}), 400

    team = None
    # Check by access code
    team = get_team_by_code(identifier)
    
    # If not found, check by team name or id
    if not team:
        with db_session() as conn:
            cursor = conn.cursor()
            if identifier.isdigit():
                cursor.execute("SELECT * FROM teams WHERE id = ?", (int(identifier),))
            else:
                cursor.execute("SELECT * FROM teams WHERE LOWER(team_name) = ?", (identifier.lower(),))
            row = cursor.fetchone()
            if row:
                team = dict(row)

    if not team:
        return jsonify({"success": False, "message": "Squad not found. Check the squad name or access code."}), 404

    session["team_id"] = team["id"]
    resume_info = get_team_resume_target(team["id"])
    return jsonify({
        "success": True,
        "message": f"Active squad switched to: {team['team_name']}",
        "team": team,
        "resume_url": resume_info["resume_url"],
        "resume_label": resume_info["resume_label"],
        "is_started": resume_info["is_started"]
    })

@game_bp.route("/api/teams", methods=["GET"])
def api_list_teams():
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, team_name, access_code, score, stars, coins, current_world FROM teams ORDER BY score DESC, stars DESC")
        teams = [dict(row) for row in cursor.fetchall()]
    return jsonify(teams)

@game_bp.route("/api/team/status")
def team_status():
    team = get_current_team()
    return jsonify({
        "id": team["id"],
        "name": team["team_name"],
        "score": team["score"],
        "coins": team["coins"],
        "stars": team["stars"],
        "current_world": team["current_world"]
    })

