# Database tables for teams, challenges, flags, and game state.

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, UniqueConstraint, Index, func
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def to_utc_iso(dt):
    """
    Guarantees consistent UTC ISO formatting with explicit timezone indicator (+00:00 or Z).
    Prevents JavaScript Date parser from misinterpreting naive timestamps as local time (e.g. 5.5h IST skew).
    """
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

_to_utc_iso = to_utc_iso


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String(100), unique=True, nullable=False, index=True)
    access_code = Column(String(64), unique=True, nullable=False, index=True)
    student_name = Column(String(100), nullable=True)
    register_number = Column(String(64), nullable=True, index=True)
    phone_number = Column(String(32), nullable=True)
    score = Column(Integer, default=0, nullable=False, index=True)
    coins = Column(Integer, default=100, nullable=False)
    stars = Column(Integer, default=0, nullable=False, index=True)  # Normal-case stars (0-11)
    current_world = Column(Integer, default=1, nullable=False)
    run_state = Column(String(20), default="STANDBY", nullable=False)  # STANDBY, ACTIVE, COMPLETED
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    total_time = Column(String(32), nullable=True)
    last_challenge_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_active = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    solves = relationship("SolvedChallenge", back_populates="team", cascade="all, delete-orphan")
    hints = relationship("HintUnlocked", back_populates="team", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="team", cascade="all, delete-orphan")
    boss_progress = relationship("BossProgress", back_populates="team", uselist=False, cascade="all, delete-orphan")
    ledger_entries = relationship("ScoreLedger", back_populates="team", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "team_name": self.team_name,
            "student_name": self.student_name,
            "register_number": self.register_number,
            "phone_number": self.phone_number,
            "access_code": self.access_code,
            "score": self.score,
            "coins": self.coins,
            "stars": self.stars,
            "current_world": self.current_world,
            "run_state": self.run_state,
            "started_at": to_utc_iso(self.started_at),
            "finished_at": to_utc_iso(self.finished_at),
            "total_time": self.total_time,
            "last_challenge_id": self.last_challenge_id,
            "created_at": to_utc_iso(self.created_at),
            "last_active": to_utc_iso(self.last_active),
        }


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    member_name = Column(String(100), nullable=False)
    session_id = Column(String(128), nullable=False, index=True)
    ip_address = Column(String(64), nullable=True)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_active = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    team = relationship("Team", back_populates="members")

    __table_args__ = (
        Index("ix_team_member_session", "team_id", "session_id"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "team_id": self.team_id,
            "member_name": self.member_name,
            "joined_at": to_utc_iso(self.joined_at),
            "last_active": to_utc_iso(self.last_active),
        }


class World(Base):
    __tablename__ = "worlds"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    subtitle = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    theme_color = Column(String(32), nullable=False)
    icon = Column(String(16), nullable=False)
    required_stars = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)

    challenges = relationship("Challenge", back_populates="world", order_by="Challenge.id")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "subtitle": self.subtitle,
            "description": self.description,
            "theme_color": self.theme_color,
            "icon": self.icon,
            "required_stars": self.required_stars,
            "is_active": self.is_active,
            "order_index": self.order_index,
        }


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    slug = Column(String(64), unique=True, nullable=False, index=True)
    category = Column(String(64), nullable=False)
    difficulty = Column(String(32), nullable=False)
    points = Column(Integer, nullable=False)
    coins_reward = Column(Integer, nullable=False)
    star_reward = Column(Integer, default=1, nullable=False)
    description = Column(Text, nullable=False)
    forensic_brief = Column(Text, nullable=False)
    interactive_type = Column(String(64), nullable=False)
    flag_hash = Column(String(128), nullable=False)
    salt = Column(String(64), nullable=False)
    hint_1 = Column(Text, nullable=False)
    hint_1_cost = Column(Integer, default=20, nullable=False)
    hint_2 = Column(Text, nullable=False)
    hint_2_cost = Column(Integer, default=40, nullable=False)

    world = relationship("World", back_populates="challenges")
    solves = relationship("SolvedChallenge", back_populates="challenge")

    def to_dict(self, mask_hints=False, mask_secrets=True):
        data = {
            "id": self.id,
            "world_id": self.world_id,
            "title": self.title,
            "slug": self.slug,
            "category": self.category,
            "difficulty": self.difficulty,
            "points": self.points,
            "coins_reward": self.coins_reward,
            "star_reward": self.star_reward,
            "description": self.description,
            "forensic_brief": self.forensic_brief,
            "interactive_type": self.interactive_type,
            "hint_1_cost": self.hint_1_cost,
            "hint_2_cost": self.hint_2_cost,
        }
        if not mask_hints:
            data["hint_1"] = self.hint_1
            data["hint_2"] = self.hint_2
        if not mask_secrets:
            data["flag_hash"] = self.flag_hash
            data["salt"] = self.salt
        return data


class SolvedChallenge(Base):
    __tablename__ = "solved_challenges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False, index=True)
    awarded_points = Column(Integer, nullable=False)
    awarded_coins = Column(Integer, nullable=False)
    awarded_stars = Column(Integer, nullable=False)
    solved_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    team = relationship("Team", back_populates="solves")
    challenge = relationship("Challenge", back_populates="solves")

    __table_args__ = (
        UniqueConstraint("team_id", "challenge_id", name="uq_team_challenge_solve"),
    )


class ScoreLedger(Base):
    __tablename__ = "score_ledger"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    delta_points = Column(Integer, nullable=False)
    delta_coins = Column(Integer, nullable=False)
    delta_stars = Column(Integer, nullable=False)
    source = Column(String(64), nullable=False)  # CHALLENGE_SOLVE, HINT_UNLOCK, ADMIN_ADJUST
    reference_id = Column(Integer, nullable=True)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    team = relationship("Team", back_populates="ledger_entries")


class HintUnlocked(Base):
    __tablename__ = "hints_unlocked"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False, index=True)
    hint_num = Column(Integer, nullable=False)
    cost_paid = Column(Integer, nullable=False)
    unlocked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    team = relationship("Team", back_populates="hints")

    __table_args__ = (
        UniqueConstraint("team_id", "challenge_id", "hint_num", name="uq_team_challenge_hint"),
    )


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False, index=True)
    flag_attempt = Column(String(255), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    ip_address = Column(String(64), nullable=True)
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    team = relationship("Team", back_populates="submissions")


class BossProgress(Base):
    __tablename__ = "boss_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # Stage 1: 4 Sector Keycodes
    stage1_shield1 = Column(Boolean, default=False, nullable=False)  # SECRET
    stage1_shield2 = Column(Boolean, default=False, nullable=False)  # PINES
    stage1_shield3 = Column(Boolean, default=False, nullable=False)  # BOO
    stage1_shield4 = Column(Boolean, default=False, nullable=False)  # INSIDER
    stage1_completed = Column(Boolean, default=False, nullable=False)

    # Stage 2: Cybersecurity Trivia Check
    stage2_q1 = Column(Boolean, default=False, nullable=False)  # nmap
    stage2_q2 = Column(Boolean, default=False, nullable=False)  # =
    stage2_q3 = Column(Boolean, default=False, nullable=False)  # AES
    stage2_q4 = Column(Boolean, default=False, nullable=False)  # Buffer Overflow
    stage2_completed = Column(Boolean, default=False, nullable=False)

    # Stage 3: Master Flag (FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION})
    stage3_completed = Column(Boolean, default=False, nullable=False)

    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    team = relationship("Team", back_populates="boss_progress")

    def to_dict(self):
        return {
            "team_id": self.team_id,
            "stage1_complete": self.stage1_completed,
            "stage2_complete": self.stage2_completed,
            "stage3_complete": self.stage3_completed,
            "stage1_shield1": self.stage1_shield1,
            "stage1_shield2": self.stage1_shield2,
            "stage1_shield3": self.stage1_shield3,
            "stage1_shield4": self.stage1_shield4,
            "stage1": {
                "shield1": self.stage1_shield1,
                "shield2": self.stage1_shield2,
                "shield3": self.stage1_shield3,
                "shield4": self.stage1_shield4,
                "completed": self.stage1_completed,
            },
            "stage2": {
                "q1": self.stage2_q1,
                "q2": self.stage2_q2,
                "q3": self.stage2_q3,
                "q4": self.stage2_q4,
                "completed": self.stage2_completed,
            },
            "stage3": {
                "completed": self.stage3_completed,
            },
            "current_stage": 3 if self.stage2_completed else (2 if self.stage1_completed else 1)
        }


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)


class CompetitionState(Base):
    __tablename__ = "competition_state"

    id = Column(Integer, primary_key=True, default=1)
    status = Column(String(32), default="LOBBY", nullable=False)  # LOBBY, ACTIVE, PAUSED, ENDED
    title = Column(String(128), default="OJAS 2026: Mario Cybersecurity CTF", nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    announcement = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "title": self.title,
            "started_at": to_utc_iso(self.started_at),
            "ended_at": to_utc_iso(self.ended_at),
            "announcement": self.announcement,
            "updated_at": to_utc_iso(self.updated_at),
        }

