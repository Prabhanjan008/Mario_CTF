"""
Authoritative Leaderboard & Standings Service.
Implements deterministic ranking rules:
1. Total score DESC
2. Normal-case stars DESC
3. Is finished (COMPLETED first)
4. Total elapsed completion time ASC
5. Recorded finish timestamp ASC (deterministic tie-breaker)
"""

import csv
import io
from datetime import datetime, timezone
from models.db import db_session
from models.schema import Team, SolvedChallenge, to_utc_iso
from services.run_service import get_team_run_info, format_duration


def get_leaderboard_standings() -> list:
    """
    Computes real-time standings across all registered squads.
    Calculates elapsed times server-side without fabricating finished times for active teams.
    """
    with db_session() as sess:
        teams = sess.query(Team).all()

        # Count solves per team
        solves_counts = {}
        for s in sess.query(SolvedChallenge.team_id, SolvedChallenge.challenge_id).all():
            solves_counts.setdefault(s[0], set()).add(s[1])

        standings = []
        now = datetime.now(timezone.utc)

        for t in teams:
            t_dict = t.to_dict()
            run_info = get_team_run_info(t)
            solved_set = solves_counts.get(t.id, set())

            # Normal stars = solves among 1..11
            normal_solves_count = sum(1 for cid in solved_set if cid < 12)
            boss_solved = 12 in solved_set

            # Elapsed seconds calculation
            is_completed = (t.run_state == "COMPLETED" and t.finished_at is not None)
            if is_completed:
                started = t.started_at
                if started and started.tzinfo is None:
                    started = started.replace(tzinfo=timezone.utc)
                finished = t.finished_at
                if finished and finished.tzinfo is None:
                    finished = finished.replace(tzinfo=timezone.utc)
                elapsed_sec = int((finished - started).total_seconds()) if (finished and started) else 999999
                time_display = t.total_time or format_duration(elapsed_sec)
                sort_time = elapsed_sec
            elif t.started_at:
                started = t.started_at
                if started.tzinfo is None:
                    started = started.replace(tzinfo=timezone.utc)
                elapsed_sec = int((now - started).total_seconds())
                time_display = f"{format_duration(elapsed_sec)} [ACTIVE]"
                sort_time = 10000000 + elapsed_sec  # Active teams sort after completed teams
            else:
                elapsed_sec = 0
                time_display = "STANDBY"
                sort_time = 20000000

            finish_iso = to_utc_iso(t.finished_at) or "9999-99-99"

            t_dict.update({
                "solved_count": len(solved_set),
                "normal_stars": normal_solves_count,
                "boss_solved": boss_solved,
                "is_completed": is_completed,
                "display_time": time_display,
                "sort_time": sort_time,
                "total_time_seconds": elapsed_sec,
                "finish_sort": finish_iso,
                "run_info": run_info
            })
            standings.append(t_dict)

        # Deterministic Sorting
        standings.sort(
            key=lambda x: (
                -x["score"],                     # 1. Total score DESC
                -x["normal_stars"],              # 2. Normal stars DESC
                0 if x["is_completed"] else 1,   # 3. Completed teams first
                x["sort_time"],                  # 4. Total elapsed seconds ASC
                x["finish_sort"],                # 5. Recorded finish timestamp ASC (tie-breaker)
                x["id"]                          # 6. ID ASC
            )
        )

        for rank_idx, item in enumerate(standings, start=1):
            item["rank"] = rank_idx

        return standings


def generate_leaderboard_csv() -> str:
    """Generates RFC-4180 compliant CSV export of official standings."""
    standings = get_leaderboard_standings()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Rank", "Team Name", "Access Code", "Score (PTS)", "Normal Stars",
        "Coins", "Solves", "Run State", "Total Elapsed Time", "Registered At", "Last Active"
    ])

    for row in standings:
        writer.writerow([
            row["rank"],
            row["team_name"],
            row["access_code"],
            row["score"],
            row["normal_stars"],
            row["coins"],
            row["solved_count"],
            row["run_state"],
            row["display_time"],
            row["created_at"],
            row["last_active"]
        ])

    return output.getvalue()


def generate_leaderboard_json() -> dict:
    """Generates structured JSON export of official standings and metadata."""
    standings = get_leaderboard_standings()
    return {
        "event": "OJAS Tech Fest 2026 - Chanakya University",
        "game": "Mario: The Cyber Heist CTF",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "total_teams": len(standings),
        "standings": standings
    }
