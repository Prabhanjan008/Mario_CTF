# Tracks elapsed time for each player from start to finish.

from datetime import datetime, timezone
from models.db import db_session
from models.schema import Team, SolvedChallenge, BossProgress, AuditLog, to_utc_iso

def format_duration(total_seconds: int) -> str:
    """Formats integer seconds into HH:MM:SS."""
    if total_seconds < 0:
        total_seconds = 0
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_team_run_info(team: Team) -> dict:
    """
    Computes authoritative timer telemetry strictly on the server.
    Immune to client clock skew or tampering.
    """
    now = datetime.now(timezone.utc)

    if team.run_state == "STANDBY" or not team.started_at:
        return {
            "run_state": "STANDBY",
            "is_started": False,
            "is_completed": False,
            "elapsed_seconds": 0,
            "formatted_time": "00:00:00",
            "timer_badge": "⏱️ 00:00:00 [READY]",
            "started_at": None,
            "finished_at": None,
        }

    # Ensure team.started_at has UTC timezone info
    started = team.started_at
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)

    if team.run_state == "COMPLETED" or team.finished_at:
        finished = team.finished_at
        if finished and finished.tzinfo is None:
            finished = finished.replace(tzinfo=timezone.utc)

        duration = int((finished - started).total_seconds()) if finished else 0
        frozen_str = team.total_time or format_duration(duration)

        return {
            "run_state": "COMPLETED",
            "is_started": True,
            "is_completed": True,
            "elapsed_seconds": duration,
            "formatted_time": frozen_str,
            "total_time": frozen_str,
            "timer_badge": f"🏆 {frozen_str} [COMPLETED]",
            "started_at": to_utc_iso(started),
            "finished_at": to_utc_iso(finished),
        }

    # ACTIVE run
    elapsed = int((now - started).total_seconds())
    formatted = format_duration(elapsed)
    return {
        "run_state": "ACTIVE",
        "is_started": True,
        "is_completed": False,
        "elapsed_seconds": elapsed,
        "formatted_time": formatted,
        "timer_badge": f"⏱️ {formatted} [ACTIVE]",
        "started_at": to_utc_iso(started),
        "finished_at": None,
    }


def start_team_run(team_id: int, ip: str = None) -> dict:
    """
    Explicit, state-changing POST endpoint to start the squad's competition timer.
    Fully idempotent: concurrent calls or retries NEVER reset an active timer.
    """
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"success": False, "message": "Team not found."}

        # Idempotent: already running or completed
        if team.run_state in ("ACTIVE", "COMPLETED") and team.started_at is not None:
            info = get_team_run_info(team)
            return {
                "success": True,
                "message": "Run already active.",
                "run_info": info,
                "already_started": True
            }

        now = datetime.now(timezone.utc)
        team.started_at = now
        team.run_state = "ACTIVE"
        team.last_active = now

        audit = AuditLog(
            team_id=team.id,
            action="RUN_STARTED",
            details="Competition timer officially triggered upon challenge engagement.",
            ip_address=ip
        )
        sess.add(audit)
        sess.flush()

        info = get_team_run_info(team)
        return {
            "success": True,
            "message": "Competition clock started!",
            "run_info": info,
            "already_started": False
        }


def complete_team_run(team, sess=None, ip: str = None, trigger_reason: str = None) -> dict:
    """
    Freezes the competition clock upon successful verification of the final boss flag.
    Atomically writes finished_at, total_time, and updates run_state to COMPLETED.
    """
    if not team:
        return {"success": False, "message": "Team not found.", "formatted_time": "00:00:00"}
    if isinstance(team, int):
        with db_session(sess) as s:
            t = s.query(Team).filter_by(id=team).first()
            if not t:
                return {"success": False, "message": "Team not found.", "formatted_time": "00:00:00"}
            return complete_team_run(t, sess=s, ip=ip, trigger_reason=trigger_reason)

    now = datetime.now(timezone.utc)
    if team.run_state == "COMPLETED" and team.finished_at:
        info = get_team_run_info(team)
        info["success"] = True
        return info

    started = team.started_at or now
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)

    duration = int((now - started).total_seconds())
    formatted = format_duration(duration)

    team.finished_at = now
    team.total_time = formatted
    team.run_state = "COMPLETED"
    team.last_active = now

    audit = AuditLog(
        team_id=team.id,
        action="RUN_COMPLETED",
        details=f"Team completed full mission in {formatted}!",
        ip_address=ip
    )
    if sess:
        sess.add(audit)

    info = get_team_run_info(team)
    info["success"] = True
    return info


def reopen_team_run(team_id: int, admin_ip: str = None) -> dict:
    """Administrative action: reopens a finished run and unfreezes timer."""
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"success": False, "message": "Team not found."}

        team.finished_at = None
        team.total_time = None
        team.run_state = "ACTIVE" if team.started_at else "STANDBY"

        audit = AuditLog(
            team_id=team.id,
            action="RUN_REOPENED",
            details="Administrator reopened mission clock.",
            ip_address=admin_ip
        )
        sess.add(audit)
        sess.flush()

        return {
            "success": True,
            "message": f"Run reopened for team '{team.team_name}'.",
            "run_info": get_team_run_info(team)
        }


def get_team_resume_target(team_id: int) -> dict:
    """
    Determines where the squad left off and returns the optimal resume URL.
    Crash-proof and device-switch friendly.
    """
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {
                "is_started": False,
                "is_finished": False,
                "challenge_id": 1,
                "resume_url": "/briefing",
                "resume_label": "Case 1: The Broken Notice Board"
            }

        run_info = get_team_run_info(team)
        if run_info["is_completed"]:
            return {
                "is_started": True,
                "is_finished": True,
                "is_champion": True,
                "challenge_id": 12,
                "challenge_title": "Mecha-Shellshock Defeated",
                "resume_url": "/victory",
                "resume_label": f"Victory Ceremony (Locked: {run_info['formatted_time']})",
                "world_id": 5,
                "world_name": "Final Fortress"
            }

        # Check for recorded solves
        solved_ids = {s.challenge_id for s in sess.query(SolvedChallenge).filter_by(team_id=team.id).all()}
        has_progress = bool(solved_ids or team.last_challenge_id or team.started_at or team.run_state == "ACTIVE")

        # If not started and no recorded progress yet
        if not has_progress and not run_info["is_started"]:
            return {
                "is_started": False,
                "is_finished": False,
                "challenge_id": 1,
                "resume_url": "/briefing",
                "resume_label": "Start Case 1: The Broken Notice Board"
            }

        # Check in order 1..12
        for c_id in range(1, 13):
            if c_id not in solved_ids:
                # Target found
                return {
                    "is_started": True,
                    "is_finished": False,
                    "challenge_id": c_id,
                    "resume_url": f"/challenge/{c_id}",
                    "resume_label": f"Resume Case {c_id}"
                }

        return {
            "is_started": True,
            "is_finished": False,
            "challenge_id": 12,
            "resume_url": "/challenge/12",
            "resume_label": "Case 12: Final Boss Arena"
        }
