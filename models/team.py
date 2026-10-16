"""
Team Model & Operations (Refactored to SQLAlchemy).
Delegates to dedicated services and models.schema.Team for concurrency and persistence.
"""

from datetime import datetime, timezone
from models.db import db_session
from models.schema import Team, TeamMember, BossProgress, AuditLog, ScoreLedger
from services.auth_service import register_team as svc_register_team, generate_team_access_code
from services.run_service import (
    start_team_run, complete_team_run, reopen_team_run,
    get_team_run_info, get_team_resume_target
)
from services.leaderboard_service import get_leaderboard_standings


def get_or_create_default_team():
    with db_session() as sess:
        team = sess.query(Team).filter_by(access_code="MARIO-OJAS-2026").first()
        if not team:
            team = sess.query(Team).order_by(Team.id.asc()).first()
        if not team:
            team = Team(
                team_name="Inspector Mario",
                access_code="MARIO-OJAS-2026",
                score=0,
                coins=100,
                stars=0,
                current_world=1,
                run_state="STANDBY"
            )
            sess.add(team)
            sess.flush()
            bp = BossProgress(team_id=team.id)
            sess.add(bp)
            sess.flush()
        return team.to_dict()


def get_team_by_id(team_id: int):
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        return team.to_dict() if team else None


def get_team_by_code(access_code: str):
    clean = access_code.strip().upper()
    with db_session() as sess:
        team = sess.query(Team).filter_by(access_code=clean).first()
        return team.to_dict() if team else None


def register_team(team_name: str):
    res = svc_register_team(team_name)
    if res["success"]:
        return res["team"]
    return None


def update_team_name(team_id: int, new_name: str):
    cleaned = new_name.strip()
    if not cleaned:
        return {"success": False, "message": "Team name cannot be empty."}

    with db_session() as sess:
        existing = sess.query(Team).filter(Team.team_name.ilike(cleaned), Team.id != team_id).first()
        if existing:
            return {"success": False, "message": f"Team name '{cleaned}' is already taken by another squad."}

        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"success": False, "message": "Team not found."}

        team.team_name = cleaned
        team.last_active = datetime.now(timezone.utc)
        sess.flush()
        return {"success": True, "team": team.to_dict()}


def update_team_score(team_id: int, points: int, coins: int, stars: int, conn=None):
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if team:
            team.score += points
            team.coins += coins
            team.stars += stars
            team.last_active = datetime.now(timezone.utc)
            if team.stars >= 11:
                team.current_world = 5
            elif team.stars >= 8:
                team.current_world = 4
            elif team.stars >= 5:
                team.current_world = 3
            elif team.stars >= 2:
                team.current_world = 2
            else:
                team.current_world = 1
            sess.flush()
            return team.to_dict()
    return None


def deduct_coins(team_id: int, amount: int, conn=None) -> bool:
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team or team.coins < amount:
            return False
        team.coins -= amount
        team.last_active = datetime.now(timezone.utc)
        sess.flush()
        return True


def start_team_timer(team_id: int):
    res = start_team_run(team_id)
    return res.get("run_info")


def finish_team_timer(team_id: int):
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if team:
            res = complete_team_run(team, sess=sess)
            return res
    return None


def reopen_team_mission(team_id: int):
    res = reopen_team_run(team_id)
    return res.get("run_info")


def get_leaderboard():
    return get_leaderboard_standings()


def update_team_last_challenge(team_id: int, challenge_id: int):
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if team:
            team.last_challenge_id = challenge_id
            team.last_active = datetime.now(timezone.utc)
