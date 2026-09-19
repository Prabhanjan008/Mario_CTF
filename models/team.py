import uuid
from datetime import datetime
from models.db import get_db_connection, db_session

def get_or_create_default_team():
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams WHERE id = 1 OR access_code = 'MARIO-OJAS-2026' ORDER BY id ASC LIMIT 1")
        team = cursor.fetchone()
        if not team:
            cursor.execute("SELECT * FROM teams ORDER BY id ASC LIMIT 1")
            team = cursor.fetchone()
        if not team:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO teams (team_name, access_code, score, coins, stars, current_world, created_at, last_active)
                VALUES ('Inspector Mario', 'MARIO-OJAS-2026', 0, 100, 0, 1, ?, ?)
            """, (now_str, now_str))
            cursor.execute("SELECT * FROM teams ORDER BY id ASC LIMIT 1")
            team = cursor.fetchone()
        return dict(team)

def get_team_by_id(team_id: int):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        team = cursor.fetchone()
        return dict(team) if team else None

def get_team_by_code(access_code: str):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams WHERE access_code = ?", (access_code.strip(),))
        team = cursor.fetchone()
        return dict(team) if team else None

def register_team(team_name: str):
    access_code = f"OJAS-{uuid.uuid4().hex[:6].upper()}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO teams (team_name, access_code, score, coins, stars, current_world, created_at, last_active)
            VALUES (?, ?, 0, 100, 0, 1, ?, ?)
        """, (team_name.strip(), access_code, now_str, now_str))
        team_id = cursor.lastrowid
        cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        return dict(cursor.fetchone())

def update_team_name(team_id: int, new_name: str):
    cleaned = new_name.strip()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM teams WHERE team_name = ? AND id != ?", (cleaned, team_id))
        if cursor.fetchone():
            return {"success": False, "message": f"Team name '{cleaned}' is already taken by another squad."}
        cursor.execute("UPDATE teams SET team_name = ? WHERE id = ?", (cleaned, team_id))
        cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        return {"success": True, "team": dict(cursor.fetchone())}

def _apply_team_score(conn, team_id: int, points: int, coins: int, stars: int):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE teams
        SET score = score + ?,
            coins = coins + ?,
            stars = stars + ?,
            last_active = ?
        WHERE id = ?
    """, (points, coins, stars, now_str, team_id))
    
    cursor.execute("SELECT stars FROM teams WHERE id = ?", (team_id,))
    row = cursor.fetchone()
    total_stars = row["stars"] if row else 0

    current_world = 1
    if total_stars >= 11:
        current_world = 5
    elif total_stars >= 8:
        current_world = 4
    elif total_stars >= 5:
        current_world = 3
    elif total_stars >= 2:
        current_world = 2

    cursor.execute("UPDATE teams SET current_world = ? WHERE id = ?", (current_world, team_id))

def update_team_score(team_id: int, points: int, coins: int, stars: int, conn=None):
    if conn is not None:
        _apply_team_score(conn, team_id, points, coins, stars)
    else:
        with db_session() as c:
            _apply_team_score(c, team_id, points, coins, stars)

def _apply_deduct_coins(conn, team_id: int, cost: int) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT coins FROM teams WHERE id = ?", (team_id,))
    row = cursor.fetchone()
    if not row or row["coins"] < cost:
        return False
    cursor.execute("UPDATE teams SET coins = coins - ? WHERE id = ?", (cost, team_id))
    return True

def deduct_coins(team_id: int, cost: int, conn=None) -> bool:
    if conn is not None:
        return _apply_deduct_coins(conn, team_id, cost)
    else:
        with db_session() as c:
            return _apply_deduct_coins(c, team_id, cost)

def start_team_timer(team_id: int):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE teams
            SET started_at = ?
            WHERE id = ? AND started_at IS NULL
        """, (now_str, team_id))
        cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def finish_team_timer(team_id: int):
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT started_at, finished_at FROM teams WHERE id = ?", (team_id,))
        row = cursor.fetchone()
        if not row or row["finished_at"] is not None:
            return None

        started_str = row["started_at"]
        total_time_str = "00:00:00"
        if started_str:
            try:
                started_dt = datetime.strptime(started_str, "%Y-%m-%d %H:%M:%S")
                elapsed_secs = max(0, int((now - started_dt).total_seconds()))
                h = elapsed_secs // 3600
                m = (elapsed_secs % 3600) // 60
                s = elapsed_secs % 60
                total_time_str = f"{h:02d}:{m:02d}:{s:02d}"
            except Exception:
                pass

        cursor.execute("""
            UPDATE teams
            SET finished_at = ?, total_time = ?
            WHERE id = ? AND finished_at IS NULL
        """, (now_str, total_time_str, team_id))
        cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        updated = cursor.fetchone()
        return dict(updated) if updated else None

def get_leaderboard():
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, team_name, score, coins, stars, current_world, started_at, finished_at, total_time, last_active
            FROM teams
            ORDER BY score DESC, stars DESC,
                     CASE WHEN finished_at IS NOT NULL THEN 0 ELSE 1 END,
                     CASE WHEN total_time IS NOT NULL THEN total_time ELSE '999:99:99' END ASC,
                     last_active ASC
        """)
        return [dict(row) for row in cursor.fetchall()]

def update_team_last_challenge(team_id: int, challenge_id: int):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE teams
            SET last_challenge_id = ?,
                last_active = ?
            WHERE id = ?
        """, (challenge_id, now_str, team_id))

def get_team_resume_target(team_id: int) -> dict:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        team = cursor.fetchone()
        if not team:
            return {
                "is_started": False,
                "is_finished": False,
                "challenge_id": 1,
                "resume_url": "/briefing",
                "resume_label": "Case 1: The Broken Notice Board"
            }
        
        team = dict(team)
        
        # Check if finished
        cursor.execute("SELECT COUNT(*) as solved_total FROM solved_challenges WHERE team_id = ?", (team_id,))
        solved_total = cursor.fetchone()["solved_total"]
        if team.get("finished_at") is not None or solved_total >= 12 or team.get("stars", 0) >= 12:
            return {
                "is_started": True,
                "is_finished": True,
                "challenge_id": 12,
                "challenge_title": "Master Key Synthesis: The Mecha-Shellshock Showdown",
                "resume_url": "/victory",
                "resume_label": "Victory Ceremony (All 12 Cases Solved!)",
                "world_id": 5,
                "world_name": "Final Fortress"
            }
            
        is_started = bool(team.get("started_at") or team.get("last_challenge_id") or team.get("stars", 0) > 0)
        if not is_started:
            return {
                "is_started": False,
                "is_finished": False,
                "challenge_id": 1,
                "challenge_title": "The Broken Notice Board",
                "resume_url": "/briefing",
                "resume_label": "Case 1: The Broken Notice Board"
            }
            
        target_challenge_id = team.get("last_challenge_id")
        
        # Check if target_challenge_id is already solved
        target_is_solved = False
        if target_challenge_id:
            cursor.execute("SELECT id FROM solved_challenges WHERE team_id = ? AND challenge_id = ?", (team_id, target_challenge_id))
            target_is_solved = bool(cursor.fetchone())
            
        # If no last challenge or if that challenge was solved, find next unsolved challenge
        if not target_challenge_id or target_is_solved:
            cursor.execute("""
                SELECT c.id FROM challenges c
                LEFT JOIN solved_challenges sc ON c.id = sc.challenge_id AND sc.team_id = ?
                WHERE sc.id IS NULL
                ORDER BY c.id ASC
                LIMIT 1
            """, (team_id,))
            nxt = cursor.fetchone()
            if nxt:
                target_challenge_id = nxt["id"]
            else:
                target_challenge_id = 12

        cursor.execute("""
            SELECT c.id, c.title, c.world_id, w.name as world_name, w.required_stars
            FROM challenges c
            JOIN worlds w ON c.world_id = w.id
            WHERE c.id = ?
        """, (target_challenge_id,))
        ch = cursor.fetchone()
        
        if ch:
            user_stars = team.get("stars", 0)
            if user_stars >= ch["required_stars"]:
                resume_url = f"/challenge/{ch['id']}"
            else:
                resume_url = "/map"
                
            return {
                "is_started": True,
                "is_finished": False,
                "challenge_id": ch["id"],
                "challenge_title": ch["title"],
                "world_id": ch["world_id"],
                "world_name": ch["world_name"],
                "resume_url": resume_url,
                "resume_label": f"Case {ch['id']}: {ch['title']} ({ch['world_name']})"
            }
            
        return {
            "is_started": True,
            "is_finished": False,
            "challenge_id": 1,
            "challenge_title": "The Broken Notice Board",
            "resume_url": "/challenge/1",
            "resume_label": "Case 1: The Broken Notice Board (Mushroom Village)"
        }

