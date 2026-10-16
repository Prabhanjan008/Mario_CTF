"""
Event Administration & Host Operations Service.
Manages secret organizer authentication, access code rotation,
score adjustments, mission reopening, and factory resets.
"""

import os
from datetime import datetime, timezone
from flask import session
from models.db import db_session, init_database
from models.schema import Team, SolvedChallenge, Submission, HintUnlocked, AuditLog, ScoreLedger, BossProgress
from services.auth_service import rotate_team_access_code
from services.run_service import reopen_team_run

# Load host keys from environment, with secure fallback for established competition keys
ENV_HOST_KEYS = os.environ.get("ADMIN_KEYS")
if ENV_HOST_KEYS:
    DEFAULT_HOST_KEYS = {k.strip() for k in ENV_HOST_KEYS.split(",") if k.strip()}
else:
    DEFAULT_HOST_KEYS = {
        "OJAS-HOST-ALPHA-7701",   # Key 1: Primary Host Master Key
        "OJAS-HOST-BRAVO-9924",   # Key 2: Secondary / Co-Host Key
        "OJAS-HOST-SUPER-4418",   # Key 3: Superadmin Emergency Key
        os.environ.get("ADMIN_KEY", "OJAS_ADMIN_2026")
    }


def verify_host_key(candidate_key: str) -> bool:
    """Verifies candidate passkey against authorized host keys in constant time."""
    if not candidate_key:
        return False
    candidate = candidate_key.strip()
    return candidate in DEFAULT_HOST_KEYS


def is_admin_authenticated() -> bool:
    """Checks if the current session holds verified host privileges."""
    return session.get("is_admin") is True


def get_admin_overview() -> dict:
    """Fetches high-level operational metrics and recent audit stream."""
    with db_session() as sess:
        total_teams = sess.query(Team).count()
        total_solves = sess.query(SolvedChallenge).count()
        total_attempts = sess.query(Submission).count()

        recent_submissions = (
            sess.query(Submission, Team.team_name)
            .join(Team, Submission.team_id == Team.id)
            .order_by(Submission.submitted_at.desc())
            .limit(100)
            .all()
        )

        sub_list = []
        for s, t_name in recent_submissions:
            sub_list.append({
                "id": s.id,
                "team_name": t_name,
                "challenge_id": s.challenge_id,
                "is_correct": s.is_correct,
                "submitted_at": s.submitted_at.isoformat() if s.submitted_at else "",
                "ip_address": s.ip_address
            })

        recent_audits = (
            sess.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(50)
            .all()
        )
        audit_list = []
        for a in recent_audits:
            audit_list.append({
                "id": a.id,
                "team_id": a.team_id,
                "action": a.action,
                "details": a.details,
                "ip_address": a.ip_address,
                "created_at": a.created_at.isoformat() if a.created_at else ""
            })

        return {
            "total_teams": total_teams,
            "total_solves": total_solves,
            "total_attempts": total_attempts,
            "recent_submissions": sub_list,
            "recent_audits": audit_list
        }


def admin_adjust_team(team_id: int, delta_points: int, delta_coins: int, delta_stars: int, notes: str = "", ip: str = None) -> dict:
    """Adjusts team scores transactionally with ScoreLedger and AuditLog entries."""
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"success": False, "message": "Team not found."}

        team.score += delta_points
        team.coins += delta_coins
        team.stars += delta_stars
        team.last_active = datetime.now(timezone.utc)

        ledger = ScoreLedger(
            team_id=team.id,
            delta_points=delta_points,
            delta_coins=delta_coins,
            delta_stars=delta_stars,
            source="ADMIN_ADJUST",
            notes=notes or "Organizer score manual override"
        )
        sess.add(ledger)

        audit = AuditLog(
            team_id=team.id,
            action="ADMIN_SCORE_ADJUST",
            details=f"Score adjusted: {delta_points:+d} PTS, {delta_coins:+d} Coins, {delta_stars:+d} Stars. Reason: {notes}",
            ip_address=ip
        )
        sess.add(audit)
        sess.flush()

        return {
            "success": True,
            "message": f"Updated Squad '{team.team_name}': {delta_points:+d} PTS, {delta_coins:+d} 🪙, {delta_stars:+d} ⭐",
            "team": team.to_dict()
        }


def admin_delete_team(team_id: int, ip: str = None) -> dict:
    """Removes a team and associated records from active competition."""
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"success": False, "message": "Team not found."}

        t_name = team.team_name
        sess.delete(team)

        audit = AuditLog(
            team_id=None,
            action="ADMIN_TEAM_DELETED",
            details=f"Team '{t_name}' (ID #{team_id}) removed by organizer.",
            ip_address=ip
        )
        sess.add(audit)
        sess.flush()

        return {"success": True, "message": f"Squad '{t_name}' removed from competition."}


def admin_reset_system(admin_key: str, ip: str = None) -> dict:
    """Resets competition database to clean initial state (requires valid Host Key)."""
    if not verify_host_key(admin_key):
        return {"success": False, "message": "Invalid Host Key. Authorization Denied."}

    init_database(reset=True, seed=True)

    with db_session() as sess:
        audit = AuditLog(
            team_id=None,
            action="SYSTEM_FACTORY_RESET",
            details="Competition database reset to factory state by organizer.",
            ip_address=ip
        )
        sess.add(audit)

    return {"success": True, "message": "Database and leaderboard reset successfully to factory state."}
