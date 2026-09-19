import hashlib
from datetime import datetime
from models.db import get_db_connection, db_session
from models.team import update_team_score, deduct_coins

def hash_flag(flag: str, salt: str) -> str:
    cleaned = flag.strip()
    return hashlib.sha256(f"{cleaned}:{salt}".encode("utf-8")).hexdigest()

def get_worlds_with_status(team_id: int):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM worlds ORDER BY id ASC")
        worlds = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT stars, current_world FROM teams WHERE id = ?", (team_id,))
        team_row = cursor.fetchone()
        team_stars = team_row["stars"] if team_row else 0

        # Get solved challenges count per world
        cursor.execute("""
            SELECT c.world_id, COUNT(sc.id) as solved_count, COUNT(c.id) as total_challenges
            FROM challenges c
            LEFT JOIN solved_challenges sc ON c.id = sc.challenge_id AND sc.team_id = ?
            GROUP BY c.world_id
        """, (team_id,))
        stats = {row["world_id"]: dict(row) for row in cursor.fetchall()}

        for w in worlds:
            w_id = w["id"]
            stat = stats.get(w_id, {"solved_count": 0, "total_challenges": 0})
            w["solved_count"] = stat["solved_count"]
            w["total_challenges"] = stat["total_challenges"]
            w["is_unlocked"] = (team_stars >= w["required_stars"])
            w["is_completed"] = (stat["solved_count"] > 0 and stat["solved_count"] == stat["total_challenges"])
        
        return worlds

def get_challenges_by_world(world_id: int, team_id: int):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM challenges WHERE world_id = ? ORDER BY id ASC", (world_id,))
        challenges = [dict(row) for row in cursor.fetchall()]

        cursor.execute("""
            SELECT challenge_id FROM solved_challenges WHERE team_id = ?
        """, (team_id,))
        solved_ids = {row["challenge_id"] for row in cursor.fetchall()}

        cursor.execute("""
            SELECT challenge_id, hint_num FROM hints_unlocked WHERE team_id = ?
        """, (team_id,))
        unlocked_hints = {}
        for row in cursor.fetchall():
            unlocked_hints.setdefault(row["challenge_id"], set()).add(row["hint_num"])

        for c in challenges:
            c_id = c["id"]
            c["is_solved"] = c_id in solved_ids
            c["hints_unlocked"] = list(unlocked_hints.get(c_id, set()))
            # Remove flag_hash and salt from output to prevent frontend scraping
            c.pop("flag_hash", None)
            c.pop("salt", None)

        return challenges

def get_challenge_detail(challenge_id: int, team_id: int):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM challenges WHERE id = ?", (challenge_id,))
        c = cursor.fetchone()
        if not c:
            return None
        c = dict(c)

        cursor.execute("SELECT * FROM worlds WHERE id = ?", (c["world_id"],))
        world = cursor.fetchone()
        c["world"] = dict(world) if world else None

        cursor.execute("SELECT * FROM solved_challenges WHERE team_id = ? AND challenge_id = ?", (team_id, challenge_id))
        solved = cursor.fetchone()
        c["is_solved"] = bool(solved)

        cursor.execute("SELECT hint_num FROM hints_unlocked WHERE team_id = ? AND challenge_id = ?", (team_id, challenge_id))
        unlocked = {row["hint_num"] for row in cursor.fetchall()}
        c["hints_unlocked"] = list(unlocked)

        # Mask hints that aren't unlocked
        if 1 not in unlocked:
            c["hint_1"] = None
        if 2 not in unlocked:
            c["hint_2"] = None

        # Fetch all challenges in this world with solved state
        cursor.execute("SELECT id, title, points, coins_reward, star_reward, interactive_type FROM challenges WHERE world_id = ? ORDER BY id ASC", (c["world_id"],))
        w_challenges = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT challenge_id FROM solved_challenges WHERE team_id = ?", (team_id,))
        all_solved_ids = {row["challenge_id"] for row in cursor.fetchall()}
        
        for ch in w_challenges:
            ch["is_solved"] = ch["id"] in all_solved_ids
        c["world_challenges"] = w_challenges

        # Determine next and prev challenge IDs
        c_ids = [ch["id"] for ch in w_challenges]
        cur_idx = c_ids.index(challenge_id) if challenge_id in c_ids else -1
        
        c["prev_challenge_id"] = c_ids[cur_idx - 1] if cur_idx > 0 else None
        
        if cur_idx >= 0 and cur_idx < len(c_ids) - 1:
            c["next_challenge_id"] = c_ids[cur_idx + 1]
            c["next_challenge_title"] = w_challenges[cur_idx + 1]["title"]
        else:
            # Check next world first challenge if unlocked
            cursor.execute("SELECT stars FROM teams WHERE id = ?", (team_id,))
            team_stars = cursor.fetchone()["stars"]
            cursor.execute("SELECT id, name, required_stars FROM worlds WHERE id = ?", (c["world_id"] + 1,))
            next_w = cursor.fetchone()
            if next_w and team_stars >= next_w["required_stars"]:
                cursor.execute("SELECT id, title FROM challenges WHERE world_id = ? ORDER BY id ASC LIMIT 1", (next_w["id"],))
                nxt_c = cursor.fetchone()
                c["next_challenge_id"] = nxt_c["id"] if nxt_c else None
                c["next_challenge_title"] = f"{next_w['name']}: {nxt_c['title']}" if nxt_c else None
            else:
                c["next_challenge_id"] = None
                c["next_challenge_title"] = None

        # Mask flag hashes
        c.pop("flag_hash", None)
        c.pop("salt", None)

        return c

def verify_and_solve_flag(team_id: int, challenge_id: int, flag_attempt: str):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM challenges WHERE id = ?", (challenge_id,))
        c = cursor.fetchone()
        if not c:
            return {"success": False, "message": "Challenge not found"}

        # Check if already solved
        cursor.execute("SELECT id FROM solved_challenges WHERE team_id = ? AND challenge_id = ?", (team_id, challenge_id))
        if cursor.fetchone():
            return {"success": False, "message": "Challenge already solved by your team!", "already_solved": True}

        # Check flag hash
        attempt_hash = hash_flag(flag_attempt, c["salt"])
        is_correct = (attempt_hash == c["flag_hash"])

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log submission
        cursor.execute("""
            INSERT INTO submissions (team_id, challenge_id, flag_attempt, is_correct, submitted_at)
            VALUES (?, ?, ?, ?, ?)
        """, (team_id, challenge_id, flag_attempt.strip(), 1 if is_correct else 0, now_str))

        if not is_correct:
            return {"success": False, "message": "Incorrect Flag. Check your investigation clues and try again!"}

        # Award score, coins, stars
        cursor.execute("""
            INSERT INTO solved_challenges (team_id, challenge_id, awarded_points, awarded_coins, awarded_stars, solved_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (team_id, challenge_id, c["points"], c["coins_reward"], c["star_reward"], now_str))

        update_team_score(team_id, c["points"], c["coins_reward"], c["star_reward"], conn=conn)

        # Check total solved count & updated team stars
        cursor.execute("SELECT stars, current_world FROM teams WHERE id = ?", (team_id,))
        team_row = cursor.fetchone()
        total_stars = team_row["stars"]
        current_world = team_row["current_world"]

        cursor.execute("SELECT COUNT(*) as total_solved FROM solved_challenges WHERE team_id = ?", (team_id,))
        total_solved = cursor.fetchone()["total_solved"]

        # Check if next challenge in current world exists
        cursor.execute("""
            SELECT id FROM challenges 
            WHERE world_id = ? AND id > ? 
            ORDER BY id ASC LIMIT 1
        """, (c["world_id"], challenge_id))
        next_in_world = cursor.fetchone()

        # Check if current world is now 100% completed
        cursor.execute("SELECT COUNT(*) as total_in_w FROM challenges WHERE world_id = ?", (c["world_id"],))
        total_in_w = cursor.fetchone()["total_in_w"]
        cursor.execute("""
            SELECT COUNT(*) as solved_in_w FROM solved_challenges sc
            JOIN challenges ch ON sc.challenge_id = ch.id
            WHERE sc.team_id = ? AND ch.world_id = ?
        """, (team_id, c["world_id"]))
        solved_in_w = cursor.fetchone()["solved_in_w"]
        is_world_completed = (solved_in_w >= total_in_w)

        # Check if next world unlocked
        next_world_id = c["world_id"] + 1
        cursor.execute("SELECT * FROM worlds WHERE id = ?", (next_world_id,))
        next_world = cursor.fetchone()
        next_world_unlocked = bool(next_world and total_stars >= next_world["required_stars"])

        next_challenge_id = None
        next_challenge_url = None

        if next_in_world:
            next_challenge_id = next_in_world["id"]
            next_challenge_url = f"/challenge/{next_challenge_id}"
        elif next_world_unlocked and next_world:
            cursor.execute("SELECT id FROM challenges WHERE world_id = ? ORDER BY id ASC LIMIT 1", (next_world_id,))
            nxt_c = cursor.fetchone()
            if nxt_c:
                next_challenge_id = nxt_c["id"]
                next_challenge_url = f"/challenge/{next_challenge_id}"
        elif challenge_id == 12:
            next_challenge_url = "/victory"

        return {
            "success": True,
            "message": f"MISSION COMPLETED! Correct flag verified. +{c['points']} Points, +{c['coins_reward']} Coins, +{c['star_reward']} Star!",
            "points_awarded": c["points"],
            "coins_awarded": c["coins_reward"],
            "stars_awarded": c["star_reward"],
            "total_solved": total_solved,
            "total_stars": total_stars,
            "next_challenge_id": next_challenge_id,
            "next_challenge_url": next_challenge_url or "/map",
            "is_world_completed": is_world_completed,
            "next_world_unlocked": next_world_unlocked,
            "next_world_id": next_world["id"] if next_world else None,
            "next_world_name": next_world["name"] if next_world else None
        }

def unlock_hint(team_id: int, challenge_id: int, hint_num: int):
    if hint_num not in (1, 2):
        return {"success": False, "message": "Invalid hint index"}

    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM challenges WHERE id = ?", (challenge_id,))
        c = cursor.fetchone()
        if not c:
            return {"success": False, "message": "Challenge not found"}

        cost = c["hint_1_cost"] if hint_num == 1 else c["hint_2_cost"]
        hint_text = c["hint_1"] if hint_num == 1 else c["hint_2"]

        # Check if already unlocked
        cursor.execute("SELECT id FROM hints_unlocked WHERE team_id = ? AND challenge_id = ? AND hint_num = ?", (team_id, challenge_id, hint_num))
        if cursor.fetchone():
            return {"success": True, "hint": hint_text, "already_unlocked": True}

        # Attempt to deduct coins
        if not deduct_coins(team_id, cost, conn=conn):
            return {"success": False, "message": f"Insufficient coins. You need {cost} coins for this forensic hint."}

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO hints_unlocked (team_id, challenge_id, hint_num, cost_paid, unlocked_at)
            VALUES (?, ?, ?, ?, ?)
        """, (team_id, challenge_id, hint_num, cost, now_str))

        return {
            "success": True,
            "hint": hint_text,
            "cost_paid": cost,
            "message": f"Hint {hint_num} unlocked for {cost} coins."
        }
