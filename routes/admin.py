import os
import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, Response
from models.db import db_session
from models.team import get_leaderboard, update_team_score
from database.init_db import init_db

admin_bp = Blueprint("admin", __name__)

# ==========================================
# 3 HARDCODED SECRET HOST KEYS
# Host/Organizer access only - NEVER shared with players!
# ==========================================
HOST_SECRET_KEYS = {
    "OJAS-HOST-ALPHA-7701",   # Key 1: Primary Host Master Key
    "OJAS-HOST-BRAVO-9924",   # Key 2: Secondary / Co-Host Key
    "OJAS-HOST-SUPER-4418",   # Key 3: Superadmin Emergency Key
}
LEGACY_ADMIN_KEY = os.environ.get("ADMIN_KEY", "OJAS_ADMIN_2026")
ALL_VALID_HOST_KEYS = HOST_SECRET_KEYS | {LEGACY_ADMIN_KEY}

def is_admin_authenticated():
    return session.get("is_admin") is True

@admin_bp.route("/admin", methods=["GET", "POST"])
def admin_panel():
    error = None
    if request.method == "POST":
        key = request.form.get("admin_key", "").strip()
        if key in ALL_VALID_HOST_KEYS:
            session["is_admin"] = True
            return redirect(url_for("admin.admin_panel"))
        else:
            error = "Invalid Host Security Key. Access Denied."

    if not is_admin_authenticated():
        return render_template("admin_login.html", error=error)

    with db_session() as conn:
        cursor = conn.cursor()

        # 1. Fetch all 12 challenges
        cursor.execute("""
            SELECT id, world_id, title, category, difficulty, points, coins_reward
            FROM challenges
            ORDER BY id ASC
        """)
        challenges = [dict(r) for r in cursor.fetchall()]

        # 2. Fetch all teams ordered by score and stars
        cursor.execute("""
            SELECT id, team_name, access_code, score, coins, stars, current_world, created_at, last_active
            FROM teams
            ORDER BY score DESC, stars DESC, last_active ASC
        """)
        teams = [dict(r) for r in cursor.fetchall()]

        # 3. Solved challenges map per team
        cursor.execute("SELECT team_id, challenge_id, solved_at FROM solved_challenges")
        solves_by_team = {}
        for row in cursor.fetchall():
            solves_by_team.setdefault(row["team_id"], {})[row["challenge_id"]] = row["solved_at"]

        # 4. Failed submissions count per team
        cursor.execute("SELECT team_id, COUNT(*) as failed_count FROM submissions WHERE is_correct = 0 GROUP BY team_id")
        failed_counts = {row["team_id"]: row["failed_count"] for row in cursor.fetchall()}

        # Enrich teams with progress stats
        total_challenges_count = len(challenges) or 12
        for rank_idx, t in enumerate(teams, start=1):
            t["rank"] = rank_idx
            team_solves = solves_by_team.get(t["id"], {})
            t["solved_ids"] = list(team_solves.keys())
            t["solved_count"] = len(team_solves)
            t["failed_count"] = failed_counts.get(t["id"], 0)
            t["completion_pct"] = round((t["solved_count"] / total_challenges_count) * 100, 1)

        # 5. Recent 100 submissions audit log
        cursor.execute("""
            SELECT s.*, t.team_name, c.title as challenge_title
            FROM submissions s
            JOIN teams t ON s.team_id = t.id
            JOIN challenges c ON s.challenge_id = c.id
            ORDER BY s.submitted_at DESC
            LIMIT 100
        """)
        submissions = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT COUNT(*) as total_teams FROM teams")
        total_teams = cursor.fetchone()["total_teams"]

        cursor.execute("SELECT COUNT(*) as total_solves FROM solved_challenges")
        total_solves = cursor.fetchone()["total_solves"]

        cursor.execute("SELECT COUNT(*) as total_attempts FROM submissions")
        total_attempts = cursor.fetchone()["total_attempts"]

    return render_template(
        "admin.html",
        challenges=challenges,
        teams=teams,
        submissions=submissions,
        total_teams=total_teams,
        total_solves=total_solves,
        total_attempts=total_attempts
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

    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, team_name, access_code, score, stars, coins, current_world, created_at, last_active
            FROM teams
            ORDER BY score DESC, stars DESC, last_active ASC
        """)
        teams = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT team_id, COUNT(*) as solve_count FROM solved_challenges GROUP BY team_id")
        solves = {r["team_id"]: r["solve_count"] for r in cursor.fetchall()}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Rank", "Team Name", "Access Code", "Score (PTS)", "Stars", "Coins", "Solved Count", "Current Sector", "Registered At", "Last Active"])

    for idx, t in enumerate(teams, start=1):
        writer.writerow([
            idx,
            t["team_name"],
            t["access_code"],
            t["score"],
            t["stars"],
            t["coins"],
            solves.get(t["id"], 0),
            f"Sector {t['current_world']}",
            t["created_at"],
            t["last_active"]
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=ojas_ctf_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

@admin_bp.route("/api/admin/export/json")
def export_results_json():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, team_name, access_code, score, stars, coins, current_world, created_at, last_active
            FROM teams
            ORDER BY score DESC, stars DESC
        """)
        teams = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT team_id, challenge_id, solved_at FROM solved_challenges")
        solves = {}
        for r in cursor.fetchall():
            solves.setdefault(r["team_id"], []).append({
                "challenge_id": r["challenge_id"],
                "solved_at": r["solved_at"]
            })

    results = []
    for idx, t in enumerate(teams, start=1):
        t["rank"] = idx
        t["solved_challenges"] = solves.get(t["id"], [])
        results.append(t)

    return jsonify({
        "event": "OJAS Tech Fest 2026 - Chanakya University",
        "game": "Mario: The Cyber Heist CTF",
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_teams": len(results),
        "standings": results
    })

# ==========================================
# HOST CONTROLS & MANAGEMENT APIS
# ==========================================
@admin_bp.route("/api/admin/team/adjust", methods=["POST"])
def admin_adjust_team():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    data = request.get_json() or {}
    team_id = data.get("team_id")
    points = int(data.get("points", 0))
    coins = int(data.get("coins", 0))
    stars = int(data.get("stars", 0))

    if not team_id:
        return jsonify({"success": False, "message": "Missing team_id"}), 400

    update_team_score(team_id, points, coins, stars)
    return jsonify({"success": True, "message": f"Updated Squad #{team_id}: {points:+d} PTS, {coins:+d} 🪙, {stars:+d} ⭐"})

@admin_bp.route("/api/admin/team/delete", methods=["POST"])
def admin_delete_team():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    data = request.get_json() or {}
    team_id = data.get("team_id")
    if not team_id:
        return jsonify({"success": False, "message": "Missing team_id"}), 400

    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM solved_challenges WHERE team_id = ?", (team_id,))
        cursor.execute("DELETE FROM submissions WHERE team_id = ?", (team_id,))
        cursor.execute("DELETE FROM hints_unlocked WHERE team_id = ?", (team_id,))
        cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
    return jsonify({"success": True, "message": f"Squad #{team_id} removed."})

@admin_bp.route("/api/admin/reset", methods=["POST"])
def admin_reset():
    data = request.get_json(silent=True) or {}
    key = data.get("admin_key", "").strip()
    if not is_admin_authenticated() and key not in ALL_VALID_HOST_KEYS:
        return jsonify({"success": False, "message": "Unauthorized. Valid Host Key or active admin session required."}), 403

    init_db(reset=True)
    session.pop("team_id", None)
    return jsonify({"success": True, "message": "Database and leaderboard successfully reset to factory state (0 Points / Standby)."})

@admin_bp.route("/api/admin/grant-all-stars", methods=["POST"])
def admin_grant_stars():
    if not is_admin_authenticated():
        return jsonify({"success": False, "message": "Unauthorized. Admin session required."}), 403
    data = request.get_json() or {}
    team_id = data.get("team_id", 1)
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE teams SET stars = 12, coins = 1000, current_world = 5 WHERE id = ?", (team_id,))
    return jsonify({"success": True, "message": "Developer mode: Granted 12 stars and unlocked all sectors."})
