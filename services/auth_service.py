"""
Authentication & Squad Management Service.
Handles cryptographically secure access code generation, team member binding,
anti-brute-force rate limiting, and CSRF protection.
"""

import os
import secrets
import string
import time
from datetime import datetime, timezone
from collections import defaultdict
from flask import session, request, has_request_context
from sqlalchemy import func
from models.db import db_session
from models.schema import Team, TeamMember, BossProgress, AuditLog

# Unambiguous Crockford Base32 characters (no 0, 1, I, O to prevent transcription errors)
CODE_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"

# In-memory sliding window rate-limiter for join attempts: {ip: [timestamps]}
_JOIN_RATE_LIMITS = defaultdict(list)
JOIN_MAX_ATTEMPTS = 10
JOIN_WINDOW_SECONDS = 60

# In-memory sliding window rate-limiter for flag submissions: {team_id: [timestamps]}
_FLAG_RATE_LIMITS = defaultdict(list)
FLAG_MAX_ATTEMPTS = 6
FLAG_WINDOW_SECONDS = 10


def generate_team_access_code() -> str:
    """Generates a high-entropy access code: OJAS-XXXXXXXX (32^8 > 1 trillion combinations)."""
    suffix = "".join(secrets.choice(CODE_CHARS) for _ in range(8))
    return f"OJAS-{suffix}"


def check_rate_limit(store: dict, key: str, max_attempts: int, window_seconds: int) -> bool:
    """Returns True if within limits, False if rate limited."""
    now = time.time()
    cutoff = now - window_seconds
    timestamps = [t for t in store.get(key, []) if t > cutoff]
    if len(timestamps) >= max_attempts:
        store[key] = timestamps
        return False
    timestamps.append(now)
    store[key] = timestamps
    return True


def get_client_ip(req) -> str:
    """Extracts client IP respecting proxy headers if trusted."""
    forwarded = req.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return req.remote_addr or "127.0.0.1"


# ==========================================
# CSRF PROTECTION
# ==========================================
def get_or_create_csrf_token() -> str:
    """Generates a secure random CSRF token stored in the user's session."""
    if not has_request_context():
        return secrets.token_hex(32)
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_hex(32)
        session["csrf_token"] = token
    return token


def validate_csrf(req) -> bool:
    """
    Validates CSRF token from header X-CSRFToken or form field csrf_token.
    Safe HTTP methods (GET, HEAD, OPTIONS) bypass validation.
    """
    if req.method in ("GET", "HEAD", "OPTIONS"):
        return True

    if not has_request_context():
        return True

    expected = session.get("csrf_token")
    if not expected:
        return False

    received = req.headers.get("X-CSRFToken") or req.headers.get("X-CSRF-Token")
    if not received and req.form:
        received = req.form.get("csrf_token")
    if not received and req.is_json:
        data = req.get_json(silent=True) or {}
        received = data.get("csrf_token")

    if not received:
        return False

    return secrets.compare_digest(str(expected), str(received))


# ==========================================
# SQUAD REGISTRATION & JOINING
# ==========================================
def register_team(
    team_name: str,
    member_name: str = "Agent",
    register_number: str = None,
    phone_number: str = None,
    ip: str = None
) -> dict:
    """
    Registers a new individual operative with their Full Name, Register Number,
    optional Phone Number, and unique access code.
    """
    cleaned_name = team_name.strip()
    if not cleaned_name or len(cleaned_name) < 2:
        return {"success": False, "message": "Operative name must be at least 2 characters long."}
    if len(cleaned_name) > 60:
        return {"success": False, "message": "Operative name cannot exceed 60 characters."}

    clean_reg = register_number.strip().upper() if register_number else None
    clean_phone = phone_number.strip() if phone_number else None

    with db_session() as sess:
        # Check if Register Number already registered
        if clean_reg:
            existing_reg = sess.query(Team).filter(func.upper(Team.register_number) == clean_reg).first()
            if existing_reg:
                return {
                    "success": False,
                    "message": f"Register Number '{clean_reg}' is already registered (Access Code: {existing_reg.access_code}). Please resume using your access code or register number."
                }

        # Formulate display name: e.g. "Rahul Sharma (CU2026042)" if register number provided
        if clean_reg and f"({clean_reg})" not in cleaned_name:
            display_name = f"{cleaned_name} ({clean_reg})"
        else:
            display_name = cleaned_name

        # Check case-insensitive uniqueness of display name
        existing = sess.query(Team).filter(Team.team_name.ilike(display_name)).first()
        if existing:
            return {"success": False, "message": f"Operative / Squad name '{display_name}' is already taken."}

        # Generate unique access code
        for _ in range(10):
            code = generate_team_access_code()
            if not sess.query(Team).filter_by(access_code=code).first():
                break
        else:
            return {"success": False, "message": "Failed to generate unique operative access code. Please try again."}

        new_team = Team(
            team_name=display_name,
            student_name=cleaned_name,
            register_number=clean_reg,
            phone_number=clean_phone,
            access_code=code,
            score=0,
            coins=100,
            stars=0,
            current_world=1,
            run_state="STANDBY"
        )
        sess.add(new_team)
        sess.flush()

        # Initialize Boss Progress
        bp = BossProgress(team_id=new_team.id)
        sess.add(bp)

        # Register creator as first team member
        sess_id = session.get("session_id") if has_request_context() else None
        if not sess_id:
            sess_id = secrets.token_hex(24)
        if has_request_context():
            session["session_id"] = sess_id

        actual_member = member_name.strip() if (member_name and member_name.strip()) else cleaned_name
        member = TeamMember(
            team_id=new_team.id,
            member_name=actual_member,
            session_id=sess_id,
            ip_address=ip
        )
        sess.add(member)

        # Log audit
        audit = AuditLog(
            team_id=new_team.id,
            action="TEAM_REGISTERED",
            details=f"Operative '{display_name}' (Reg: {clean_reg}) registered with access code {code}",
            ip_address=ip
        )
        sess.add(audit)
        sess.flush()

        if has_request_context():
            session["team_id"] = new_team.id
            session["member_name"] = member.member_name

        return {
            "success": True,
            "message": f"Operative '{display_name}' registered successfully!",
            "team": new_team.to_dict(),
            "member_name": member.member_name,
            "access_code": code
        }


def join_team_by_code(access_code: str, member_name: str = "Agent", ip: str = None) -> dict:
    """
    Allows an operative to resume an existing session securely using their access code or register number.
    Enforces join rate-limiting.
    """
    clean_code = access_code.strip().upper()
    if not clean_code:
        return {"success": False, "message": "Please enter a valid Access Code or Register Number."}

    # Anti-brute-force rate check
    if ip and not check_rate_limit(_JOIN_RATE_LIMITS, ip, JOIN_MAX_ATTEMPTS, JOIN_WINDOW_SECONDS):
        return {
            "success": False,
            "message": "Too many failed attempts. Please wait 1 minute before trying again."
        }

    with db_session() as sess:
        team = sess.query(Team).filter_by(access_code=clean_code).first()
        if not team:
            # Also allow finding by register number
            team = sess.query(Team).filter(func.upper(Team.register_number) == clean_code).first()

        if not team:
            return {
                "success": False,
                "message": "Invalid Access Code or Register Number. Check your credentials."
            }

        sess_id = session.get("session_id") if has_request_context() else None
        if not sess_id:
            sess_id = secrets.token_hex(24)
        if has_request_context():
            session["session_id"] = sess_id

        # Check if member already registered in this team
        existing_member = sess.query(TeamMember).filter_by(team_id=team.id, session_id=sess_id).first()
        if existing_member:
            if member_name.strip():
                existing_member.member_name = member_name.strip()
            existing_member.last_active = datetime.now(timezone.utc)
            active_name = existing_member.member_name
        else:
            active_name = member_name.strip() or f"Agent-{secrets.token_hex(2).upper()}"
            new_member = TeamMember(
                team_id=team.id,
                member_name=active_name,
                session_id=sess_id,
                ip_address=ip
            )
            sess.add(new_member)

        # Update team activity
        team.last_active = datetime.now(timezone.utc)

        audit = AuditLog(
            team_id=team.id,
            action="MEMBER_JOINED",
            details=f"Member '{active_name}' joined team '{team.team_name}'",
            ip_address=ip
        )
        sess.add(audit)
        sess.flush()

        if has_request_context():
            session["team_id"] = team.id
            session["member_name"] = active_name

        return {
            "success": True,
            "message": f"Successfully joined squad: {team.team_name}!",
            "team": team.to_dict(),
            "member_name": active_name
        }


def get_current_team_and_member(sess) -> tuple:
    """
    Authoritatively resolves current team and member context from server session.
    Returns (None, None) if the user has not registered or joined a squad yet.
    """
    team_id = session.get("team_id") if has_request_context() else None
    sess_id = session.get("session_id") if has_request_context() else None
    team = None
    member = None

    if team_id:
        team = sess.query(Team).filter_by(id=team_id).first()

    if not team:
        return None, None

    if not sess_id:
        sess_id = secrets.token_hex(24)
        if has_request_context():
            session["session_id"] = sess_id

    member = sess.query(TeamMember).filter_by(team_id=team.id, session_id=sess_id).first()
    if not member:
        m_name = (session.get("member_name") if has_request_context() else None) or "Inspector"
        member = TeamMember(
            team_id=team.id,
            member_name=m_name,
            session_id=sess_id
        )
        sess.add(member)
        sess.flush()
    else:
        member.last_active = datetime.now(timezone.utc)

    team.last_active = datetime.now(timezone.utc)
    return team, member


def rotate_team_access_code(team_id: int, admin_ip: str = None) -> dict:
    """Administrative action: rotates a team's access code securely."""
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"success": False, "message": "Team not found."}

        new_code = generate_team_access_code()
        old_code = team.access_code
        team.access_code = new_code

        audit = AuditLog(
            team_id=team.id,
            action="ACCESS_CODE_ROTATED",
            details=f"Access code rotated from {old_code} to {new_code}",
            ip_address=admin_ip
        )
        sess.add(audit)
        sess.flush()

        return {
            "success": True,
            "message": f"Access code for '{team.team_name}' rotated to: {new_code}",
            "new_access_code": new_code
        }
