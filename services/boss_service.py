"""
Three-Stage Boss Service (Case 12: Mecha-Shellshock Showdown).
Server-side state machine enforcing sequential progression:
Stage 1 (Shield Bypass) -> Stage 2 (Cyber Trivia) -> Stage 3 (Master Flag).
"""

from datetime import datetime, timezone
from models.db import db_session
from models.schema import BossProgress, Team, Challenge, SolvedChallenge, ScoreLedger, AuditLog
from database.seed_data import hash_flag
from services.run_service import complete_team_run, get_team_run_info
from services.progression_service import calculate_normal_stars, BOSS_REQUIRED_STARS

# ==========================================
# SERVER-SIDE ACCEPTED ANSWERS (NEVER SENT TO CLIENT)
# ==========================================

# Stage 1: 4 Sector Keycodes
STAGE1_KEYS = {
    1: {"SECRET"},
    2: {"PINES", "PINE"},
    3: {"BOO", "KING BOO", "KINGBOO"},
    4: {"INSIDER"}
}

# Stage 2: Cybersecurity Trivia Definitions & Answers
STAGE2_QUESTIONS = {
    1: {
        "question": "What standard cybersecurity CLI utility is used for network port scanning, host discovery, and OS fingerprinting?",
        "hint": "Widely known 4-letter port scanner developed by Gordon Lyon.",
        "accepted": {"NMAP", "NMAP.ORG"}
    },
    2: {
        "question": "What special single padding character is appended to the end of a Base64 encoded payload when the input byte count is not divisible by 3?",
        "hint": "Common mathematical symbol used for assignment/equality.",
        "accepted": {"="}
    },
    3: {
        "question": "What symmetric block cipher algorithm (128, 192, or 256 bits) was established as the US federal encryption standard by NIST in 2001?",
        "hint": "3-letter acronym replacing DES (Rijndael cipher).",
        "accepted": {"AES", "ADVANCED ENCRYPTION STANDARD"}
    },
    4: {
        "question": "What critical memory safety vulnerability occurs when a program writes more data to a memory buffer than was allocated, potentially corrupting the execution stack?",
        "hint": "Classic memory-corruption flaw commonly leveraged for control-flow hijacking.",
        "accepted": {"BUFFER OVERFLOW", "BUFFEROVERFLOW", "STACK OVERFLOW", "STACKOVERFLOW", "BUFFER-OVERFLOW"}
    }
}

FINAL_BOSS_FLAG = "FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}"


def get_or_create_boss_progress(team_id: int, sess) -> BossProgress:
    """Retrieves or creates durable boss progress row for the squad."""
    bp = sess.query(BossProgress).filter_by(team_id=team_id).first()
    if not bp:
        bp = BossProgress(team_id=team_id)
        sess.add(bp)
        sess.flush()
    return bp


def get_boss_status(team_id: int) -> dict:
    """Returns the current validated stage and shield state for client rendering."""
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"success": False, "message": "Squad not found."}

        normal_stars = calculate_normal_stars(team_id, sess)
        is_unlocked = (normal_stars >= BOSS_REQUIRED_STARS)
        bp = get_or_create_boss_progress(team_id, sess)

        # Questions metadata without accepted answers
        questions_meta = {}
        for q_id, q_data in STAGE2_QUESTIONS.items():
            solved_attr = getattr(bp, f"stage2_q{q_id}", False)
            questions_meta[q_id] = {
                "question": q_data["question"],
                "hint": q_data["hint"],
                "is_solved": solved_attr
            }

        return {
            "success": True,
            "is_unlocked": is_unlocked,
            "normal_stars": normal_stars,
            "required_stars": BOSS_REQUIRED_STARS,
            "progress": bp.to_dict(),
            "stage2_questions": questions_meta,
            "run_info": get_team_run_info(team)
        }


def submit_stage1_shield(team_id: int, shield_num: int, keycode: str, ip: str = None) -> dict:
    """
    Validates Stage 1 sector keycodes on the server without leaking answers.
    Updates shield state durable in database.
    """
    if shield_num not in (1, 2, 3, 4):
        return {"success": False, "message": "Invalid shield index (1-4)."}

    clean_code = keycode.strip().upper()
    if not clean_code:
        return {"success": False, "message": "Please enter a keycode."}

    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"success": False, "message": "Squad not found."}

        normal_stars = calculate_normal_stars(team_id, sess)
        if normal_stars < BOSS_REQUIRED_STARS:
            return {"success": False, "message": "Boss challenge is locked! You need all 11 normal stars."}

        bp = get_or_create_boss_progress(team_id, sess)

        shield_attr = f"stage1_shield{shield_num}"
        if getattr(bp, shield_attr, False):
            return {
                "success": True,
                "already_cracked": True,
                "message": f"Shield {shield_num} is already neutralized!",
                "progress": bp.to_dict()
            }

        # Validate answer against server configuration
        accepted_set = STAGE1_KEYS.get(shield_num, set())
        if clean_code not in accepted_set:
            return {
                "success": False,
                "message": f"Shield {shield_num} override rejected. Incorrect keycode."
            }

        # Mark shield cracked
        setattr(bp, shield_attr, True)

        # Check if all 4 shields are now cracked
        all_shields = (
            getattr(bp, "stage1_shield1") and
            getattr(bp, "stage1_shield2") and
            getattr(bp, "stage1_shield3") and
            getattr(bp, "stage1_shield4")
        )
        if all_shields:
            bp.stage1_completed = True

        audit = AuditLog(
            team_id=team.id,
            action="BOSS_SHIELD_CRACKED",
            details=f"Cracked Boss Shield {shield_num}. All shields cracked: {all_shields}",
            ip_address=ip
        )
        sess.add(audit)
        sess.flush()

        return {
            "success": True,
            "message": f"⚡ Shield {shield_num} Neutralized!",
            "shield_num": shield_num,
            "stage1_completed": bp.stage1_completed,
            "stage1_complete": bp.stage1_completed,
            "progress": bp.to_dict()
        }


def submit_stage2_trivia(team_id: int, q_num: int, answer: str, ip: str = None) -> dict:
    """
    Validates Stage 2 Cybersecurity Knowledge Check on the server.
    Enforces that Stage 1 must be completed before Stage 2 answers are accepted.
    """
    if q_num not in (1, 2, 3, 4):
        return {"success": False, "message": "Invalid question index (1-4)."}

    clean_ans = answer.strip().upper()
    if not clean_ans:
        return {"success": False, "message": "Answer cannot be empty."}

    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"success": False, "message": "Squad not found."}

        bp = get_or_create_boss_progress(team_id, sess)

        if not bp.stage1_completed:
            return {
                "success": False,
                "message": "Stage 1 is locked! You must neutralize all 4 Quantum Shields before accessing Core Trivia."
            }

        q_attr = f"stage2_q{q_num}"
        if getattr(bp, q_attr, False):
            return {
                "success": True,
                "already_solved": True,
                "message": f"Question {q_num} is already verified!",
                "progress": bp.to_dict()
            }

        q_info = STAGE2_QUESTIONS.get(q_num)
        if not q_info or clean_ans not in q_info["accepted"]:
            return {
                "success": False,
                "message": f"Core verification {q_num} failed: Incorrect concept answer."
            }

        setattr(bp, q_attr, True)

        all_q = (
            getattr(bp, "stage2_q1") and
            getattr(bp, "stage2_q2") and
            getattr(bp, "stage2_q3") and
            getattr(bp, "stage2_q4")
        )
        if all_q:
            bp.stage2_completed = True

        audit = AuditLog(
            team_id=team.id,
            action="BOSS_TRIVIA_SOLVED",
            details=f"Solved Boss Trivia {q_num}. Stage 2 complete: {all_q}",
            ip_address=ip
        )
        sess.add(audit)
        sess.flush()

        return {
            "success": True,
            "message": f"✅ Core Question {q_num} Verified!",
            "q_num": q_num,
            "stage2_completed": bp.stage2_completed,
            "stage2_complete": bp.stage2_completed,
            "progress": bp.to_dict()
        }


def submit_stage3_final_flag(team_id: int, flag_attempt: str, ip: str = None) -> dict:
    """
    Validates Stage 3 Master Flag submission on the server.
    Enforces strict sequence: Stage 1 AND Stage 2 must be completed!
    Atomically performs final run completion, records finished_at, freezes timer,
    and awards final score and star.
    """
    clean_flag = flag_attempt.strip()
    if not clean_flag:
        return {"success": False, "message": "Flag attempt cannot be empty."}

    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"success": False, "message": "Squad not found."}

        bp = get_or_create_boss_progress(team_id, sess)

        if not bp.stage1_completed:
            return {
                "success": False,
                "message": "Security Sequence Error: Stage 1 Quantum Shields are still active!"
            }

        if not bp.stage2_completed:
            return {
                "success": False,
                "message": "Security Sequence Error: Stage 2 Core Trivia questions are not fully verified!"
            }

        # Check if already completed
        if bp.stage3_completed and team.run_state == "COMPLETED":
            return {
                "success": True,
                "already_solved": True,
                "message": "The Golden Star has already been secured by your squad! Proceed to Victory Ceremony.",
                "redirect_url": "/victory"
            }

        challenge = sess.query(Challenge).filter_by(id=12).first()
        if not challenge:
            return {"success": False, "message": "Boss challenge configuration not found."}

        # Verify final flag hash
        attempt_hash = hash_flag(clean_flag, challenge.salt)
        if attempt_hash != challenge.flag_hash and clean_flag != FINAL_BOSS_FLAG:
            return {
                "success": False,
                "message": "Master Extraction Flag rejected. Verification signature invalid."
            }

        # Verified! Mark Stage 3 completed
        now = datetime.now(timezone.utc)
        bp.stage3_completed = True

        # Atomically complete run and freeze timer
        run_telemetry = complete_team_run(team, sess=sess, ip=ip)

        # Check if SolvedChallenge record already exists
        existing_solve = sess.query(SolvedChallenge).filter_by(team_id=team.id, challenge_id=12).first()
        if not existing_solve:
            solved_rec = SolvedChallenge(
                team_id=team.id,
                challenge_id=12,
                awarded_points=challenge.points,
                awarded_coins=challenge.coins_reward,
                awarded_stars=1,  # 1 star for defeating boss
                solved_at=now
            )
            sess.add(solved_rec)

            ledger = ScoreLedger(
                team_id=team.id,
                delta_points=challenge.points,
                delta_coins=challenge.coins_reward,
                delta_stars=1,
                source="BOSS_DEFEAT",
                reference_id=12,
                notes="Defeated Mecha-Shellshock in World 5"
            )
            sess.add(ledger)
            team.score += challenge.points
            team.coins += challenge.coins_reward
            team.stars += 1

            from sqlalchemy.exc import IntegrityError
            try:
                sess.flush()
            except IntegrityError:
                sess.rollback()
                return {
                    "success": True,
                    "message": "Mecha-Shellshock already defeated by your team! Golden Star is secured.",
                    "is_finished": True,
                    "is_completed": True,
                    "total_time": team.total_time,
                    "redirect_url": "/victory",
                    "team": team.to_dict()
                }

        audit = AuditLog(
            team_id=team.id,
            action="BOSS_DEFEATED",
            details=f"Mecha-Shellshock defeated! Finished in {team.total_time}",
            ip_address=ip
        )
        sess.add(audit)
        sess.flush()

        return {
            "success": True,
            "message": f"🎉 MECHA-SHELLSHOCK DEFEATED! Golden Star Secured in {team.total_time}! +{challenge.points} PTS, +{challenge.coins_reward} Coins!",
            "points_awarded": challenge.points,
            "coins_awarded": challenge.coins_reward,
            "stars_awarded": 1,
            "is_finished": True,
            "is_completed": True,
            "total_time": team.total_time,
            "run_info": run_telemetry,
            "redirect_url": "/victory",
            "team": team.to_dict()
        }
