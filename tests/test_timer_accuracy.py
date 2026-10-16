import pytest
from datetime import datetime, timezone, timedelta
from app import create_app
from models.db import db_session, init_database
from models.schema import Team, _to_utc_iso
from services.run_service import get_team_run_info, format_duration, start_team_run, complete_team_run

def test_to_utc_iso_serialization():
    assert _to_utc_iso(None) is None

    # Naive datetime (as stored in SQLite)
    naive = datetime(2026, 10, 16, 12, 0, 0)
    iso_str = _to_utc_iso(naive)
    assert iso_str.endswith("+00:00") or iso_str.endswith("Z")
    assert "2026-10-16T12:00:00" in iso_str

    # Aware datetime
    aware_utc = datetime(2026, 10, 16, 12, 0, 0, tzinfo=timezone.utc)
    iso_aware = _to_utc_iso(aware_utc)
    assert "+00:00" in iso_aware or "Z" in iso_aware

def test_format_duration():
    assert format_duration(0) == "00:00:00"
    assert format_duration(59) == "00:00:59"
    assert format_duration(60) == "00:01:00"
    assert format_duration(3661) == "01:01:01"
    assert format_duration(86400) == "24:00:00"

def test_timer_accuracy_elapsed_seconds():
    import uuid
    uid = uuid.uuid4().hex[:6]
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        with db_session() as sess:
            t = Team(
                team_name=f"TimerSquad_{uid}",
                access_code=f"TIME-{uid.upper()}",
                run_state="STANDBY"
            )
            sess.add(t)
            sess.flush()
            t_id = t.id

            # Standby state
            info = get_team_run_info(t)
            assert info["run_state"] == "STANDBY"
            assert info["elapsed_seconds"] == 0
            assert info["formatted_time"] == "00:00:00"

            # Start run exactly 125 seconds ago
            past_time = datetime.now(timezone.utc) - timedelta(seconds=125)
            t.started_at = past_time
            t.run_state = "ACTIVE"
            sess.flush()

            info_active = get_team_run_info(t)
            assert info_active["run_state"] == "ACTIVE"
            # Should be approximately 125 seconds, NOT 19800+ seconds (5.5h offset)
            assert 124 <= info_active["elapsed_seconds"] <= 126
            assert info_active["formatted_time"] == "00:02:05"

            # Complete run
            finish_time = past_time + timedelta(seconds=125)
            t.finished_at = finish_time
            t.total_time = "00:02:05"
            t.run_state = "COMPLETED"
            sess.flush()

            info_comp = get_team_run_info(t)
            assert info_comp["run_state"] == "COMPLETED"
            assert info_comp["is_completed"] is True
            assert info_comp["formatted_time"] == "00:02:05"
            assert info_comp["total_time"] == "00:02:05"

            # Clean up
            sess.delete(t)
            sess.flush()
