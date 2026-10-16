"""
Models package for Mario: The Cyber Heist.
Exports Base, schema models, and database session utilities.
"""

from models.db import engine, db_session, get_db, get_db_connection, init_database
from models.schema import (
    Base, Team, TeamMember, World, Challenge, SolvedChallenge,
    ScoreLedger, HintUnlocked, Submission, BossProgress, AuditLog
)

__all__ = [
    "engine",
    "db_session",
    "get_db",
    "get_db_connection",
    "init_database",
    "Base",
    "Team",
    "TeamMember",
    "World",
    "Challenge",
    "SolvedChallenge",
    "ScoreLedger",
    "HintUnlocked",
    "Submission",
    "BossProgress",
    "AuditLog",
]
