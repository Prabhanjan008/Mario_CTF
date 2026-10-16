"""
Secure Challenge Submission, Flag Verification & Scoring Service.
Handles anti-brute-force rate limiting, atomic solves, score ledger auditing,
and hint unlocking.
"""

from datetime import datetime, timezone
from models.db import db_session
from models.schema import (
    Challenge, SolvedChallenge, Submission, ScoreLedger,
    HintUnlocked, Team, AuditLog
)
from database.seed_data import hash_flag
from services.auth_service import check_rate_limit, _FLAG_RATE_LIMITS, FLAG_MAX_ATTEMPTS, FLAG_WINDOW_SECONDS
from services.progression_service import is_challenge_unlocked, calculate_normal_stars, NORMAL_CHALLENGE_IDS


def verify_and_solve_flag(team_id: int, challenge_id: int, flag_attempt: str, ip: str = None, skip_rate_limit: bool = False) -> dict:
    """
    Authoritatively validates a flag submission for a team.
    Guarantees atomic, idempotent solve recording and score awards.
    """
    clean_flag = flag_attempt.strip()
    if not clean_flag:
        return {"success": False, "message": "Flag attempt cannot be empty."}

    # Anti-brute-force rate limit per team
    if not skip_rate_limit and not check_rate_limit(_FLAG_RATE_LIMITS, str(team_id), FLAG_MAX_ATTEMPTS, FLAG_WINDOW_SECONDS):
        return {
            "success": False,
            "message": "Submission rate limit reached. Please wait a few seconds before trying again."
        }

    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"success": False, "message": "Squad not found."}

        # Check run state: disallow submissions if mission is completed
        if team.run_state == "COMPLETED":
            return {
                "success": False,
                "message": "Mission has concluded! Submissions are locked. Reopen the mission to resume.",
                "mission_completed": True
            }

        # Validate challenge exists
        challenge = sess.query(Challenge).filter_by(id=challenge_id).first()
        if not challenge:
            return {"success": False, "message": "Challenge not found."}

        # Confirm challenge is currently available
        unlocked, reason, req_stars = is_challenge_unlocked(team.id, challenge_id)
        if not unlocked:
            return {"success": False, "message": reason, "locked": True}

        # Check if already solved by this team (Anti-replay)
        already_solved = (
            sess.query(SolvedChallenge)
            .filter_by(team_id=team.id, challenge_id=challenge_id)
            .first()
        )
        if already_solved:
            return {
                "success": False,
                "message": "Challenge already solved by your squad! The Golden Star sector key is secured.",
                "already_solved": True
            }

        # Verify Flag Hash
        attempt_hash = hash_flag(clean_flag, challenge.salt)
        is_correct = (attempt_hash == challenge.flag_hash)

        # Log submission attempt
        sub = Submission(
            team_id=team.id,
            challenge_id=challenge_id,
            flag_attempt=clean_flag[:250],
            is_correct=is_correct,
            ip_address=ip
        )
        sess.add(sub)

        if not is_correct:
            sess.flush()
            return {
                "success": False,
                "message": "Incorrect Flag. Check your investigation clues and try again!"
            }

        # Correct Flag! Transactionally record solve and score
        now = datetime.now(timezone.utc)
        star_reward = challenge.star_reward if challenge.id in NORMAL_CHALLENGE_IDS else 0

        solved_record = SolvedChallenge(
            team_id=team.id,
            challenge_id=challenge_id,
            awarded_points=challenge.points,
            awarded_coins=challenge.coins_reward,
            awarded_stars=star_reward,
            solved_at=now
        )
        sess.add(solved_record)

        # Record in Score Ledger
        ledger_entry = ScoreLedger(
            team_id=team.id,
            delta_points=challenge.points,
            delta_coins=challenge.coins_reward,
            delta_stars=star_reward,
            source="CHALLENGE_SOLVE",
            reference_id=challenge_id,
            notes=f"Solved Case #{challenge_id}: {challenge.title}"
        )
        sess.add(ledger_entry)

        # Update Team Totals
        team.score += challenge.points
        team.coins += challenge.coins_reward
        team.last_active = now

        from sqlalchemy.exc import IntegrityError
        try:
            sess.flush()
        except IntegrityError:
            sess.rollback()
            return {
                "success": False,
                "message": "Challenge already solved by your squad! The Golden Star sector key is secured.",
                "already_solved": True
            }

        # Recalculate derived normal stars
        total_normal_stars = calculate_normal_stars(team.id, sess)
        team.stars = total_normal_stars

        # Update current world based on stars
        if total_normal_stars >= 11:
            team.current_world = 5
        elif total_normal_stars >= 8:
            team.current_world = 4
        elif total_normal_stars >= 5:
            team.current_world = 3
        elif total_normal_stars >= 2:
            team.current_world = 2
        else:
            team.current_world = 1

        # Check total solved
        total_solved = sess.query(SolvedChallenge).filter_by(team_id=team.id).count()

        # Audit log
        audit = AuditLog(
            team_id=team.id,
            action="FLAG_SOLVED",
            details=f"Solved Case #{challenge_id} (+{challenge.points} PTS, +{challenge.coins_reward} Coins, +{star_reward} Star)",
            ip_address=ip
        )
        sess.add(audit)
        sess.flush()

        # Determine next navigation step
        next_c = (
            sess.query(Challenge)
            .filter(Challenge.world_id == challenge.world_id, Challenge.id > challenge_id)
            .order_by(Challenge.id.asc())
            .first()
        )
        next_url = f"/challenge/{next_c.id}" if next_c else "/map"

        return {
            "success": True,
            "message": f"MISSION ACCOMPLISHED! Correct flag verified. +{challenge.points} PTS, +{challenge.coins_reward} Coins, +{star_reward} Stars!",
            "points_awarded": challenge.points,
            "coins_awarded": challenge.coins_reward,
            "stars_awarded": star_reward,
            "total_solved": total_solved,
            "total_stars": total_normal_stars,
            "next_challenge_id": next_c.id if next_c else None,
            "next_challenge_url": next_url,
            "team": team.to_dict()
        }


def unlock_hint(team_id: int, challenge_id: int, hint_num: int, ip: str = None) -> dict:
    """
    Deducts coins and unlocks progressive forensic hint in an isolated atomic transaction.
    Guarantees no double-deductions.
    """
    if hint_num not in (1, 2):
        return {"success": False, "message": "Invalid hint index."}

    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"success": False, "message": "Squad not found."}

        challenge = sess.query(Challenge).filter_by(id=challenge_id).first()
        if not challenge:
            return {"success": False, "message": "Challenge not found."}

        # Check if already unlocked
        existing = (
            sess.query(HintUnlocked)
            .filter_by(team_id=team.id, challenge_id=challenge_id, hint_num=hint_num)
            .first()
        )
        hint_text = challenge.hint_1 if hint_num == 1 else challenge.hint_2
        cost = challenge.hint_1_cost if hint_num == 1 else challenge.hint_2_cost

        if existing:
            return {
                "success": True,
                "hint": hint_text,
                "already_unlocked": True,
                "cost_paid": 0,
                "remaining_coins": team.coins
            }

        # Check coin balance
        if team.coins < cost:
            return {
                "success": False,
                "message": f"Insufficient coins! Hint {hint_num} requires {cost} 🪙 (Balance: {team.coins} 🪙)."
            }

        # Deduct coins atomically
        team.coins -= cost
        team.last_active = datetime.now(timezone.utc)

        new_hint = HintUnlocked(
            team_id=team.id,
            challenge_id=challenge_id,
            hint_num=hint_num,
            cost_paid=cost
        )
        sess.add(new_hint)

        # Record in ScoreLedger
        ledger = ScoreLedger(
            team_id=team.id,
            delta_points=0,
            delta_coins=-cost,
            delta_stars=0,
            source="HINT_UNLOCK",
            reference_id=challenge_id,
            notes=f"Unlocked Hint {hint_num} for Case #{challenge_id}"
        )
        sess.add(ledger)

        audit = AuditLog(
            team_id=team.id,
            action="HINT_UNLOCKED",
            details=f"Unlocked Hint {hint_num} for Case #{challenge_id} (-{cost} coins)",
            ip_address=ip
        )
        sess.add(audit)
        sess.flush()

        return {
            "success": True,
            "hint": hint_text,
            "cost_paid": cost,
            "remaining_coins": team.coins,
            "message": f"Forensic Hint {hint_num} unlocked for {cost} 🪙."
        }
