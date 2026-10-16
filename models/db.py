"""
Database Engine & Session Management for Mario: The Cyber Heist.
Supports both PostgreSQL (production) and SQLite (development/testing) via SQLAlchemy.
Configures WAL mode, busy timeout, and connection pooling for 100+ concurrent teams.
"""

import os
import sqlite3
import uuid
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from models.schema import Base, World, Challenge, Team, BossProgress, CompetitionState
from database.seed_data import WORLDS_SEED, CHALLENGES_SEED, hash_flag

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
DEFAULT_SQLITE_PATH = os.path.abspath(os.path.join(DB_DIR, "game.db"))

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Ensure database directory exists
    os.makedirs(DB_DIR, exist_ok=True)
    clean_path = DEFAULT_SQLITE_PATH.replace("\\", "/")
    DATABASE_URL = f"sqlite:///{clean_path}"

# Normalise Postgres URL format if provided as postgres:// (e.g. from Heroku/Render)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

IS_SQLITE = DATABASE_URL.startswith("sqlite")

# Engine Configuration
if IS_SQLITE:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"timeout": 30.0, "check_same_thread": False},
        echo=False
    )

    # Enable WAL mode and foreign keys for high concurrency on SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA busy_timeout=30000;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
else:
    # PostgreSQL production pool configuration
    engine = create_engine(
        DATABASE_URL,
        pool_size=int(os.environ.get("DB_POOL_SIZE", "20")),
        max_overflow=int(os.environ.get("DB_MAX_OVERFLOW", "30")),
        pool_timeout=float(os.environ.get("DB_POOL_TIMEOUT", "30.0")),
        pool_recycle=int(os.environ.get("DB_POOL_RECYCLE", "1800")),
        pool_pre_ping=True,
        echo=False
    )

import threading

_local = threading.local()

SessionFactory = sessionmaker(bind=engine, autoflush=True, expire_on_commit=False)
ScopedSession = scoped_session(SessionFactory)


@contextmanager
def db_session(existing_session=None):
    """
    Re-entrant, transactional context manager.
    Supports nested calls safely: outermost context performs commit/rollback and cleanup.
    """
    if existing_session is not None:
        yield existing_session
        return

    depth = getattr(_local, "depth", 0)
    _local.depth = depth + 1
    session = ScopedSession()

    try:
        yield session
        if _local.depth == 1:
            session.commit()
    except Exception:
        if _local.depth == 1:
            session.rollback()
        raise
    finally:
        _local.depth -= 1
        if _local.depth == 0:
            ScopedSession.remove()


def get_db():
    """Generator yielding a session, for route handlers or scripts."""
    session = ScopedSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        ScopedSession.remove()


def init_database(reset: bool = False, seed: bool = True):
    """
    Initialises all schema tables and seeds master worlds & challenges idempotently.
    Safe to run repeatedly without overwriting existing squad progress when reset=False.
    """
    if reset:
        Base.metadata.drop_all(bind=engine)
    
    Base.metadata.create_all(bind=engine)

    if not seed:
        return

    with db_session() as session:
        # Seed Worlds
        for w_data in WORLDS_SEED:
            existing_world = session.query(World).filter_by(id=w_data["id"]).first()
            if not existing_world:
                world = World(**w_data)
                session.add(world)
            else:
                for k, v in w_data.items():
                    setattr(existing_world, k, v)
        session.flush()

        # Seed Challenges
        for c_data in CHALLENGES_SEED:
            existing_c = session.query(Challenge).filter_by(id=c_data["id"]).first()
            salt = uuid.uuid4().hex[:16]
            f_hash = hash_flag(c_data["raw_flag"], salt)

            c_fields = {
                "id": c_data["id"],
                "world_id": c_data["world_id"],
                "title": c_data["title"],
                "slug": c_data["slug"],
                "category": c_data["category"],
                "difficulty": c_data["difficulty"],
                "points": c_data["points"],
                "coins_reward": c_data["coins_reward"],
                "star_reward": c_data.get("star_reward", 1),
                "description": c_data["description"],
                "forensic_brief": c_data["forensic_brief"],
                "interactive_type": c_data["interactive_type"],
                "hint_1": c_data["hint_1"],
                "hint_1_cost": c_data["hint_1_cost"],
                "hint_2": c_data["hint_2"],
                "hint_2_cost": c_data["hint_2_cost"],
            }

            if not existing_c:
                c_fields["flag_hash"] = f_hash
                c_fields["salt"] = salt
                ch = Challenge(**c_fields)
                session.add(ch)
            else:
                for k, v in c_fields.items():
                    setattr(existing_c, k, v)
        session.flush()

        # Seed Competition State (default to LOBBY awaiting host dispatch)
        comp_state = session.query(CompetitionState).filter_by(id=1).first()
        if not comp_state:
            comp_state = CompetitionState(
                id=1,
                status="LOBBY",
                title="OJAS 2026: Mario Cybersecurity CTF"
            )
            session.add(comp_state)
            session.flush()


# For backward compatibility with any raw sqlite tests/utilities
def get_db_connection():
    if IS_SQLITE:
        conn = sqlite3.connect(DEFAULT_SQLITE_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn
    else:
        # PostgreSQL raw connection via engine
        return engine.raw_connection()
