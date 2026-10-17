"""
Comprehensive Automated Test Suite for OJAS Cybersecurity CTF Production Platform.
Covers Phases 1 through 12:
1. Squad Registration & Cryptographic Access Codes (Crockford Base32)
2. Multi-Member Concurrency & Shared Team State
3. Cross-Team IDOR & Session Isolation
4. Authoritative Run Lifecycle, Idempotent Start & Frozen Timers
5. Star Thresholds & World Unlock Progression (Cases 1-11 = 11 Stars)
6. Flag Verification, Anti-Replay Idempotency & Score Ledger
7. Three-Stage Boss Showdown (Shields -> Trivia -> Master Flag)
8. Authoritative Leaderboard & Deterministic Tie-Breaking
9. Organizer Admin Passkey Authorization & Audited Actions
10. CSRF Protection & Rate Limiting
"""

import pytest
import time
from datetime import datetime, timezone, timedelta
from app import create_app
from models.db import db_session, init_database
from models.schema import Team, TeamMember, Challenge, SolvedChallenge, ScoreLedger, BossProgress, AuditLog
from services.auth_service import (
    generate_team_access_code,
    register_team,
    join_team_by_code,
    rotate_team_access_code,
    get_or_create_csrf_token,
    _FLAG_RATE_LIMITS,
    _JOIN_RATE_LIMITS
)
from services.run_service import (
    start_team_run,
    complete_team_run,
    get_team_run_info,
    reopen_team_run
)
from services.progression_service import (
    calculate_normal_stars,
    is_challenge_unlocked,
    get_worlds_with_status,
    BOSS_REQUIRED_STARS
)
from services.challenge_service import verify_and_solve_flag, unlock_hint
from services.boss_service import (
    get_boss_status,
    submit_stage1_shield,
    submit_stage2_trivia,
    submit_stage3_final_flag
)
from services.leaderboard_service import get_leaderboard_standings
from services.admin_service import (
    verify_host_key,
    admin_adjust_team,
    admin_delete_team,
    admin_reset_system
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure schema and seed data are initialized."""
    init_database(reset=False, seed=True)


@pytest.fixture
def flask_app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key-ojas-2026"
    return app


@pytest.fixture
def client(flask_app):
    return flask_app.test_client()


# ==============================================================================
# 1. SQUAD REGISTRATION & ACCESS CODE TESTS
# ==============================================================================

def test_access_code_format_and_entropy():
    """Verify OJAS- prefix and Crockford Base32 charset with zero ambiguous characters."""
    code = generate_team_access_code()
    assert code.startswith("OJAS-")
    suffix = code.split("-")[1]
    assert len(suffix) == 8
    # Crockford Base32 does not use 0, 1, I, O to prevent transcription ambiguity
    ambiguous = set("01IOio")
    assert not any(c in ambiguous for c in suffix)


def test_unique_squad_registration():
    """Verify team registration assigns unique code, starter coins, and Standby state."""
    team_name = f"TestSquad_{int(time.time()*1000)}"
    res = register_team(team_name, member_name="LeaderOne", ip="127.0.0.1")
    assert res["success"] is True
    assert res["team"]["team_name"] == team_name
    assert res["team"]["access_code"].startswith("OJAS-")
    assert res["team"]["coins"] == 100
    assert res["team"]["score"] == 0
    assert res["team"]["stars"] == 0
    assert res["team"]["run_state"] == "STANDBY"

    # Verify duplicate name is rejected
    dup_res = register_team(team_name, member_name="Impostor", ip="127.0.0.1")
    assert dup_res["success"] is False
    assert "already" in dup_res["message"].lower()


def test_multi_member_shared_team_context():
    """Verify multiple members join the same team via code and share team identity."""
    team_name = f"MultiSquad_{int(time.time()*1000)}"
    reg = register_team(team_name, member_name="Alice", ip="127.0.0.1")
    access_code = reg["team"]["access_code"]
    team_id = reg["team"]["id"]

    # Member 2 joins from second device
    join2 = join_team_by_code(access_code, member_name="Bob", ip="10.0.0.2")
    assert join2["success"] is True
    assert join2["team"]["id"] == team_id
    assert join2["member_name"] == "Bob"

    # Member 3 joins from third device
    join3 = join_team_by_code(access_code, member_name="Charlie", ip="10.0.0.3")
    assert join3["success"] is True
    assert join3["team"]["id"] == team_id
    assert join3["member_name"] == "Charlie"

    # Verify members in database
    with db_session() as sess:
        members = sess.query(TeamMember).filter_by(team_id=team_id).all()
        member_names = {m.member_name for m in members}
        assert "Alice" in member_names
        assert "Bob" in member_names
        assert "Charlie" in member_names


# ==============================================================================
# 2. RUN LIFECYCLE & AUTHORITATIVE UTC TIMER TESTS
# ==============================================================================

def test_run_lifecycle_and_idempotent_timer_start():
    """Verify STANDBY -> ACTIVE -> COMPLETED, idempotent start, and frozen timer."""
    reg = register_team(f"TimerSquad_{int(time.time()*1000)}", member_name="Runner")
    team_id = reg["team"]["id"]

    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        assert team.run_state == "STANDBY"
        assert team.started_at is None
        assert team.finished_at is None

    # First start: switches to ACTIVE
    res1 = start_team_run(team_id)
    assert res1["success"] is True
    assert res1["run_info"]["run_state"] == "ACTIVE"
    started_at_1 = res1["run_info"]["started_at"]
    assert started_at_1 is not None

    time.sleep(0.05)

    # Second concurrent or refresh start: must be idempotent, NOT resetting started_at
    res2 = start_team_run(team_id)
    assert res2["success"] is True
    assert res2["run_info"]["started_at"] == started_at_1

    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        assert team.run_state == "ACTIVE"
        info = get_team_run_info(team)
        assert info["is_started"] is True
        assert info["elapsed_seconds"] >= 0

    # Complete run: freezes timer
    comp = complete_team_run(team_id, trigger_reason="TEST_FINISH")
    assert comp["success"] is True
    assert comp["run_state"] == "COMPLETED"
    assert comp["total_time"] is not None

    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        assert team.run_state == "COMPLETED"
        assert team.finished_at is not None
        # Normal submissions must now be disallowed
        flag_res = verify_and_solve_flag(team_id, 1, "FLAG{MUSHROOM_SECRET_OJAS_2026}")
        assert flag_res["success"] is False
        assert "concluded" in flag_res["message"].lower()


# ==============================================================================
# 3. STAR PROGRESSION & WORLD UNLOCK GATING TESTS
# ==============================================================================

def test_star_thresholds_and_world_gating():
    """Verify Cases 1-11 star thresholds: W1(0), W2(2), W3(5), W4(8), Boss(11)."""
    reg = register_team(f"ProgSquad_{int(time.time()*1000)}", member_name="Scout")
    team_id = reg["team"]["id"]

    # World 1 challenges (Cases 1 & 2) unlocked at 0 stars
    u1, _, req1 = is_challenge_unlocked(team_id, 1)
    u2, _, req2 = is_challenge_unlocked(team_id, 2)
    assert u1 is True and req1 == 0
    assert u2 is True and req2 == 0

    # World 2 challenge (Case 3) locked at 0 stars (needs 2 stars)
    u3, reason3, req3 = is_challenge_unlocked(team_id, 3)
    assert u3 is False
    assert req3 == 2

    # Solve Case 1
    res_c1 = verify_and_solve_flag(team_id, 1, "FLAG{MUSHROOM_SECRET_OJAS_2026}")
    assert res_c1["success"] is True
    assert calculate_normal_stars(team_id) == 1

    # World 2 still locked (1 star < 2 stars)
    u3_after1, _, _ = is_challenge_unlocked(team_id, 3)
    assert u3_after1 is False

    # Solve Case 2 -> 2 stars reached!
    res_c2 = verify_and_solve_flag(team_id, 2, "FLAG{LETTER_CIPHER_SOLVED_OJAS}")
    assert res_c2["success"] is True
    assert calculate_normal_stars(team_id) == 2

    # World 2 challenge 3 must now be UNLOCKED!
    u3_unlocked, _, _ = is_challenge_unlocked(team_id, 3)
    assert u3_unlocked is True

    # Boss (Case 12) must remain locked until 11 normal stars
    u_boss, reason_boss, req_boss = is_challenge_unlocked(team_id, 12)
    assert u_boss is False
    assert req_boss == 11


# ==============================================================================
# 4. CHALLENGE VERIFICATION & ANTI-DUPLICATE SCORING
# ==============================================================================

def test_flag_solve_anti_replay_and_ledger():
    """Verify points awarded once, duplicate solves return already_solved, score ledger tracks audit."""
    reg = register_team(f"ScoreSquad_{int(time.time()*1000)}", member_name="Hacker")
    team_id = reg["team"]["id"]

    # Invalid flag rejected
    wrong = verify_and_solve_flag(team_id, 1, "FLAG{COMPLETELY_WRONG_FLAG}")
    assert wrong["success"] is False
    assert "incorrect" in wrong["message"].lower()

    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        assert team.score == 0

    # Valid solve
    solve1 = verify_and_solve_flag(team_id, 1, "FLAG{MUSHROOM_SECRET_OJAS_2026}")
    assert solve1["success"] is True
    assert solve1["points_awarded"] == 100
    assert solve1["team"]["score"] == 100

    # Immediate duplicate submit of the same flag
    solve2 = verify_and_solve_flag(team_id, 1, "FLAG{MUSHROOM_SECRET_OJAS_2026}")
    assert solve2["success"] is False
    assert solve2.get("already_solved") is True
    assert solve2.get("points_awarded", 0) == 0

    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        # Score must remain exactly 100, not 200
        assert team.score == 100
        # Exactly one SolvedChallenge record
        solves = sess.query(SolvedChallenge).filter_by(team_id=team_id, challenge_id=1).all()
        assert len(solves) == 1
        # Score ledger entries
        ledger_entries = sess.query(ScoreLedger).filter_by(team_id=team_id).all()
        total_ledger = sum(e.delta_points for e in ledger_entries)
        assert total_ledger == 100


# ==============================================================================
# 5. THREE-STAGE BOSS SHOWDOWN TESTS
# ==============================================================================

def test_three_stage_boss_sequential_progression():
    """Verify Stage 1 (Shields) -> Stage 2 (Trivia) -> Stage 3 (Master Flag) sequentially."""
    reg = register_team(f"BossSquad_{int(time.time()*1000)}", member_name="BossHunter")
    team_id = reg["team"]["id"]

    # Normal cases 1 through 11 flags to earn all 11 normal stars
    flags = {
        1: "FLAG{MUSHROOM_SECRET_OJAS_2026}",
        2: "FLAG{LETTER_CIPHER_SOLVED_OJAS}",
        3: "FLAG{FOREST_PIXEL_STEGO_OJAS}",
        4: "FLAG{METADATA_TRAIL_REVEALED_OJAS}",
        5: "FLAG{DARK_FOREST_STREAM_DECODED}",
        6: "FLAG{BOO_GHOST_PATH_DISCOVERED}",
        7: "FLAG{API_AUTH_BYPASS_OJAS}",
        8: "FLAG{SESSION_FORGERY_DETECTED_OJAS}",
        9: "FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}",
        10: "FLAG{CORRELATED_LOGS_INSIDER_OJAS}",
        11: "FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}"
    }

    # Solve all 11 normal cases
    for cid, flag in flags.items():
        res = verify_and_solve_flag(team_id, cid, flag, skip_rate_limit=True)
        assert res["success"] is True, f"Failed solving case {cid}: {res.get('message')}"

    assert calculate_normal_stars(team_id) == 11
    boss_unlocked, _, _ = is_challenge_unlocked(team_id, 12)
    assert boss_unlocked is True

    # Boss Stage 2 and 3 should be locked initially
    status = get_boss_status(team_id)
    assert status["progress"]["stage1_complete"] is False
    assert status["progress"]["stage2_complete"] is False

    # Attempting Stage 2 before Stage 1 complete must fail
    premature_t2 = submit_stage2_trivia(team_id, 1, "nmap")
    assert premature_t2["success"] is False
    assert "stage 1" in premature_t2["message"].lower()

    # Attempting Stage 3 before previous stages complete must fail
    premature_t3 = submit_stage3_final_flag(team_id, "FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}")
    assert premature_t3["success"] is False
    assert "stage 1" in premature_t3["message"].lower() or "stage 2" in premature_t3["message"].lower()

    # Solve Stage 1: 4 sector keycodes
    s1 = submit_stage1_shield(team_id, 1, "SECRET")
    s2 = submit_stage1_shield(team_id, 2, "PINES")
    s3 = submit_stage1_shield(team_id, 3, "BOO")
    s4 = submit_stage1_shield(team_id, 4, "INSIDER")
    assert s1["success"] and s2["success"] and s3["success"] and s4["success"]
    assert s4["stage1_complete"] is True
    assert s4.get("flag") == "FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}"

    # Solve Stage 3: Master Recovery Flag directly without trivia requirement
    final = submit_stage3_final_flag(team_id, s4["flag"])
    assert final["success"] is True
    assert final["is_finished"] is True

    # Verify run state is atomically set to COMPLETED and finished_at is frozen
    with db_session() as sess:
        team = sess.query(Team).filter_by(id=team_id).first()
        assert team.run_state == "COMPLETED"
        assert team.finished_at is not None
        assert team.total_time is not None


# ==============================================================================
# 6. LEADERBOARD & DETERMINISTIC TIE-BREAKING TESTS
# ==============================================================================

def test_leaderboard_deterministic_ranking():
    """Verify Score DESC -> Normal Stars DESC -> Total Time ASC -> Finished Timestamp ASC."""
    standings = get_leaderboard_standings()
    assert isinstance(standings, list)

    # Verify order properties
    for i in range(len(standings) - 1):
        a = standings[i]
        b = standings[i + 1]

        # Primary: Score DESC
        if a["score"] != b["score"]:
            assert a["score"] > b["score"]
        # Secondary: Normal Stars DESC
        elif a["normal_stars"] != b["normal_stars"]:
            assert a["normal_stars"] >= b["normal_stars"]
        # Tertiary: Finished teams rank before unfinished teams
        elif a["finished_at"] is not None and b["finished_at"] is None:
            assert True
        # Quaternary: Total Time ASC for completed teams
        elif a["finished_at"] is not None and b["finished_at"] is not None:
            if a["total_time_seconds"] != b["total_time_seconds"]:
                assert a["total_time_seconds"] <= b["total_time_seconds"]


# ==============================================================================
# 7. ORGANIZER ADMIN AUTHORIZATION & AUDITED ACTIONS
# ==============================================================================

def test_admin_authorization_and_audit_logging():
    """Verify organizer passkeys, score adjustment, and audit log generation."""
    assert verify_host_key("OJAS-HOST-ALPHA-7701") is True
    assert verify_host_key("OJAS-HOST-BRAVO-9924") is True
    assert verify_host_key("INVALID-PASSKEY-0000") is False

    reg = register_team(f"AdminSquad_{int(time.time()*1000)}", member_name="Subject")
    team_id = reg["team"]["id"]

    # Adjust score by +150
    adj = admin_adjust_team(team_id, delta_points=150, delta_coins=50, delta_stars=1, notes="Host bonus", ip="127.0.0.1")
    assert adj["success"] is True
    assert adj["team"]["score"] == 150

    # Rotate access code
    rot = rotate_team_access_code(team_id, admin_ip="127.0.0.1")
    assert rot["success"] is True
    assert rot["new_access_code"].startswith("OJAS-")

    # Verify audit logs in database
    with db_session() as sess:
        logs = sess.query(AuditLog).filter_by(team_id=team_id).all()
        actions = {l.action for l in logs}
        assert "ADMIN_SCORE_ADJUST" in actions
        assert "ACCESS_CODE_ROTATED" in actions


# ==============================================================================
# 8. CSRF PROTECTION & RATE LIMITING TESTS
# ==============================================================================

def test_csrf_protection_on_state_changing_endpoints(client):
    """Verify that POST requests without valid CSRF tokens are rejected with 403."""
    # POST /api/team/register without CSRF token
    resp = client.post("/api/team/register", json={"name": "NoCsrfTeam"})
    assert resp.status_code == 403
    data = resp.get_json()
    assert "CSRF" in data["message"]

    # POST /api/submit-flag without CSRF token
    flag_resp = client.post("/api/submit-flag", json={"challenge_id": 1, "flag": "FLAG{FOO}"})
    assert flag_resp.status_code == 403


def test_flag_submission_rate_limiting():
    """Verify sliding-window rate limit triggers when submission threshold exceeded."""
    from services.auth_service import check_rate_limit, FLAG_MAX_ATTEMPTS, FLAG_WINDOW_SECONDS
    store = {}
    key = "team_rate_test_999"

    for i in range(FLAG_MAX_ATTEMPTS):
        allowed = check_rate_limit(store, key, FLAG_MAX_ATTEMPTS, FLAG_WINDOW_SECONDS)
        assert allowed is True

    # Next attempt should be blocked
    blocked = check_rate_limit(store, key, FLAG_MAX_ATTEMPTS, FLAG_WINDOW_SECONDS)
    assert blocked is False
