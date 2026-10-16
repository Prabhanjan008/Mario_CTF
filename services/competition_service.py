"""
Authoritative Competition Lifecycle & Tournament Management Service.
Controls global competition states:
- LOBBY: Registration is open; students gather in pre-game waiting room; challenges locked.
- ACTIVE: Host has dispatched mission; timers running; full access to world map and cases.
- PAUSED: Host has temporarily paused submissions / timers.
- ENDED: Competition concluded; all submissions locked; final podium frozen.
"""

from datetime import datetime, timezone
from models.db import db_session
from models.schema import (
    CompetitionState, Team, TeamMember, SolvedChallenge,
    HintUnlocked, Submission, BossProgress, ScoreLedger, AuditLog,
    to_utc_iso
)
from services.run_service import format_duration


def get_competition_status() -> dict:
    """Retrieves current global competition status and live squad telemetry."""
    with db_session() as sess:
        state = sess.query(CompetitionState).filter_by(id=1).first()
        if not state:
            state = CompetitionState(id=1, status="LOBBY", title="OJAS 2026: Mario Cybersecurity CTF")
            sess.add(state)
            sess.flush()

        total_teams = sess.query(Team).count()
        total_members = sess.query(TeamMember).count()
        active_teams = sess.query(Team).filter_by(run_state="ACTIVE").count()
        completed_teams = sess.query(Team).filter_by(run_state="COMPLETED").count()

        now = datetime.now(timezone.utc)
        elapsed_sec = 0
        if state.started_at:
            s_at = state.started_at
            if s_at.tzinfo is None:
                s_at = s_at.replace(tzinfo=timezone.utc)
            end_at = state.ended_at or now
            if end_at.tzinfo is None:
                end_at = end_at.replace(tzinfo=timezone.utc)
            elapsed_sec = max(0, int((end_at - s_at).total_seconds()))

        return {
            "status": state.status,
            "title": state.title,
            "started_at": to_utc_iso(state.started_at),
            "ended_at": to_utc_iso(state.ended_at),
            "elapsed_seconds": elapsed_sec,
            "elapsed_formatted": format_duration(elapsed_sec),
            "announcement": state.announcement,
            "total_teams": total_teams,
            "total_members": total_members,
            "active_teams": active_teams,
            "completed_teams": completed_teams,
            "can_play": (state.status == "ACTIVE")
        }


def start_competition(admin_ip: str = None) -> dict:
    """
    Host triggers global mission dispatch.
    Transitions status to ACTIVE and starts authoritative timer for all registered squads.
    """
    with db_session() as sess:
        state = sess.query(CompetitionState).filter_by(id=1).first()
        if not state:
            state = CompetitionState(id=1, status="LOBBY")
            sess.add(state)

        now = datetime.now(timezone.utc)
        state.status = "ACTIVE"
        if not state.started_at:
            state.started_at = now
        state.ended_at = None

        # Synchronously start timer for all registered standby teams
        teams = sess.query(Team).filter_by(run_state="STANDBY").all()
        for t in teams:
            t.run_state = "ACTIVE"
            if not t.started_at:
                t.started_at = now

        audit = AuditLog(
            action="COMPETITION_STARTED",
            details=f"Host launched competition! {len(teams)} standby squads activated.",
            ip_address=admin_ip
        )
        sess.add(audit)
        sess.flush()

        return {
            "success": True,
            "status": "ACTIVE",
            "message": f"Competition started! {len(teams)} squads dispatched into the Cyber World Map.",
            "started_at": to_utc_iso(state.started_at),
            "teams_activated": len(teams)
        }


def pause_competition(admin_ip: str = None) -> dict:
    """Host temporarily pauses competition."""
    with db_session() as sess:
        state = sess.query(CompetitionState).filter_by(id=1).first()
        if not state:
            state = CompetitionState(id=1, status="LOBBY")
            sess.add(state)

        state.status = "PAUSED"
        audit = AuditLog(
            action="COMPETITION_PAUSED",
            details="Host paused the competition.",
            ip_address=admin_ip
        )
        sess.add(audit)
        sess.flush()

        return {"success": True, "status": "PAUSED", "message": "[!] Competition paused by host."}


def resume_competition(admin_ip: str = None) -> dict:
    """Host resumes paused competition."""
    with db_session() as sess:
        state = sess.query(CompetitionState).filter_by(id=1).first()
        if not state:
            state = CompetitionState(id=1, status="LOBBY")
            sess.add(state)

        state.status = "ACTIVE"
        audit = AuditLog(
            action="COMPETITION_RESUMED",
            details="Host resumed the competition.",
            ip_address=admin_ip
        )
        sess.add(audit)
        sess.flush()

        return {"success": True, "status": "ACTIVE", "message": "[+] Competition resumed!"}


def end_competition(admin_ip: str = None) -> dict:
    """Host concludes competition and freezes leaderboard."""
    with db_session() as sess:
        state = sess.query(CompetitionState).filter_by(id=1).first()
        if not state:
            state = CompetitionState(id=1, status="LOBBY")
            sess.add(state)

        now = datetime.now(timezone.utc)
        state.status = "ENDED"
        state.ended_at = now

        # Conclude any unfinished active teams
        active_teams = sess.query(Team).filter_by(run_state="ACTIVE").all()
        for t in active_teams:
            t.run_state = "COMPLETED"
            t.finished_at = now
            if t.started_at:
                s_at = t.started_at if t.started_at.tzinfo else t.started_at.replace(tzinfo=timezone.utc)
                dur = int((now - s_at).total_seconds())
                t.total_time = format_duration(dur)

        audit = AuditLog(
            action="COMPETITION_ENDED",
            details=f"Host concluded competition. {len(active_teams)} teams finalized.",
            ip_address=admin_ip
        )
        sess.add(audit)
        sess.flush()

        return {"success": True, "status": "ENDED", "message": "[*] Competition concluded! Standings frozen."}


def reset_competition_clean_slate(admin_ip: str = None) -> dict:
    """
    Purges all participant data and resets state to LOBBY.
    Does NOT seed dummy teams so real students can register from scratch.
    """
    with db_session() as sess:
        # Wipe participant progress
        sess.query(ScoreLedger).delete()
        sess.query(Submission).delete()
        sess.query(HintUnlocked).delete()
        sess.query(SolvedChallenge).delete()
        sess.query(BossProgress).delete()
        sess.query(TeamMember).delete()
        sess.query(Team).delete()

        # Reset Competition state to LOBBY
        state = sess.query(CompetitionState).filter_by(id=1).first()
        if not state:
            state = CompetitionState(id=1)
            sess.add(state)
        state.status = "LOBBY"
        state.started_at = None
        state.ended_at = None
        state.announcement = None

        audit = AuditLog(
            action="COMPETITION_CLEAN_SLATE_RESET",
            details="Purged all squads. Ready for live student event.",
            ip_address=admin_ip
        )
        sess.add(audit)
        sess.flush()

        return {
            "success": True,
            "status": "LOBBY",
            "message": "Clean slate complete! 0 squads registered. Game is in LOBBY mode ready for students."
        }


def broadcast_announcement(announcement: str, admin_ip: str = None) -> dict:
    """Updates broadcast message displayed on player screens."""
    with db_session() as sess:
        state = sess.query(CompetitionState).filter_by(id=1).first()
        if not state:
            state = CompetitionState(id=1, status="LOBBY")
            sess.add(state)

        state.announcement = announcement.strip() if announcement else None
        audit = AuditLog(
            action="HOST_BROADCAST",
            details=f"Host broadcast: {announcement}",
            ip_address=admin_ip
        )
        sess.add(audit)
        sess.flush()

        return {"success": True, "announcement": state.announcement}
