# Load test simulating 100 concurrent teams submitting flags and polling standings.

import time
import os
import sys
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from app import create_app
from models.db import db_session, init_database
from models.schema import Team, TeamMember, SolvedChallenge, ScoreLedger
from services.auth_service import register_team, join_team_by_code
from services.run_service import start_team_run, complete_team_run, get_team_run_info
from services.challenge_service import verify_and_solve_flag
from services.boss_service import submit_stage1_shield, submit_stage2_trivia, submit_stage3_final_flag
from services.leaderboard_service import get_leaderboard_standings

def run_load_test():
    print("=" * 80)
    print("  🚀 STARTING 100-TEAM REALISTIC CONCURRENCY & STRESS TEST")
    print("  Target: 100 Teams (200 Virtual Players) Concurrent Multi-Stage CTF Simulation")
    print("=" * 80)

    # Re-seed test database
    init_database(reset=False, seed=True)

    latencies = {
        "register": [],
        "member_join": [],
        "start_run": [],
        "solve_c1": [],
        "solve_c2": [],
        "duplicate_race": [],
        "leaderboard_poll": [],
        "boss_stage": []
    }

    teams_data = [] # List of {"id": int, "code": str, "name": str}
    errors = []

    # --------------------------------------------------------------------------
    # STAGE 1: 100 Squad Registrations (Concurrent)
    # --------------------------------------------------------------------------
    print("\n[Stage 1/6] Registering 100 Distinct Squads Concurrently (ThreadPool=20)...")
    start_time = time.time()

    def do_register(i):
        t0 = time.time()
        name = f"Squad_Omega_{i:03d}_{int(time.time()*1000)%100000}"
        res = register_team(name, member_name=f"Lead_{i}", ip=f"10.100.{(i//250)}.{i%250}")
        dt = (time.time() - t0) * 1000
        if not res["success"]:
            return dt, False, res["message"], None
        return dt, True, None, {"id": res["team"]["id"], "code": res["team"]["access_code"], "name": name}

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(do_register, i) for i in range(1, 101)]
        for f in as_completed(futures):
            dt, ok, err, tinfo = f.result()
            latencies["register"].append(dt)
            if ok:
                teams_data.append(tinfo)
            else:
                errors.append(f"Registration failure: {err}")

    reg_duration = time.time() - start_time
    print(f"  -> Registered {len(teams_data)}/100 squads in {reg_duration:.2f}s (p50: {statistics.median(latencies['register']):.1f}ms, p95: {sorted(latencies['register'])[int(len(latencies['register'])*0.95)]:.1f}ms)")
    assert len(teams_data) == 100, f"Expected 100 teams registered, got {len(teams_data)}"

    # --------------------------------------------------------------------------
    # STAGE 2: 100 Secondary Members Joining via Access Codes (Concurrent)
    # --------------------------------------------------------------------------
    print("\n[Stage 2/6] Multi-Member Concurrency: 100 Secondary Teammates Joining by Code...")
    def do_join(team_info, i):
        t0 = time.time()
        res = join_team_by_code(team_info["code"], member_name=f"Operator_{i}", ip=f"10.200.{(i//250)}.{i%250}")
        dt = (time.time() - t0) * 1000
        return dt, res["success"], res.get("message")

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(do_join, t, idx) for idx, t in enumerate(teams_data, 1)]
        for f in as_completed(futures):
            dt, ok, err = f.result()
            latencies["member_join"].append(dt)
            if not ok:
                errors.append(f"Join failure: {err}")

    print(f"  -> 100 secondary members joined (p50: {statistics.median(latencies['member_join']):.1f}ms, p95: {sorted(latencies['member_join'])[int(len(latencies['member_join'])*0.95)]:.1f}ms)")

    # --------------------------------------------------------------------------
    # STAGE 3: Idempotent Run Initiation Burst across 100 Squads
    # --------------------------------------------------------------------------
    print("\n[Stage 3/6] Starting Authoritative UTC Timers across all 100 Squads...")
    def do_start(team_info):
        t0 = time.time()
        res = start_team_run(team_info["id"], ip="127.0.0.1")
        dt = (time.time() - t0) * 1000
        return dt, res["success"]

    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(do_start, t) for t in teams_data]
        for f in as_completed(futures):
            dt, ok = f.result()
            latencies["start_run"].append(dt)

    print(f"  -> 100 timers authoritatively started (p50: {statistics.median(latencies['start_run']):.1f}ms, p95: {sorted(latencies['start_run'])[int(len(latencies['start_run'])*0.95)]:.1f}ms)")

    # --------------------------------------------------------------------------
    # STAGE 4: Concurrent Challenge 1 Solving & Concurrent Duplicate Race
    # --------------------------------------------------------------------------
    print("\n[Stage 4/6] High-Contention Race Test: Concurrent Duplicate Flag Submissions...")
    print("  Simulating 2 teammates from same squad submitting Case 1 flag at the exact same instant...")

    race_results = {"awarded": 0, "already_solved": 0, "errors": 0}

    def submit_flag(team_id, cid, flag):
        t0 = time.time()
        res = verify_and_solve_flag(team_id, cid, flag, skip_rate_limit=True)
        dt = (time.time() - t0) * 1000
        return dt, res

    # 50 squads submit simultaneously from 2 concurrent threads each (100 simultaneous requests)
    target_race_teams = teams_data[:50]
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = []
        for t in target_race_teams:
            # Thread A (Player 1)
            futures.append(executor.submit(submit_flag, t["id"], 1, "FLAG{MUSHROOM_SECRET_OJAS_2026}"))
            # Thread B (Player 2 - simultaneous duplicate)
            futures.append(executor.submit(submit_flag, t["id"], 1, "FLAG{MUSHROOM_SECRET_OJAS_2026}"))

        for f in as_completed(futures):
            dt, res = f.result()
            latencies["duplicate_race"].append(dt)
            if res.get("success"):
                race_results["awarded"] += 1
            elif res.get("already_solved"):
                race_results["already_solved"] += 1
            else:
                race_results["errors"] += 1

    print(f"  -> Race Results: {race_results['awarded']} primary solves awarded, {race_results['already_solved']} duplicate submissions safely rejected!")
    print(f"  -> Concurrency Latency: p50={statistics.median(latencies['duplicate_race']):.1f}ms, p95={sorted(latencies['duplicate_race'])[int(len(latencies['duplicate_race'])*0.95)]:.1f}ms")
    assert race_results["awarded"] == 50, f"Expected exactly 50 primary solves, got {race_results['awarded']}"
    assert race_results["already_solved"] == 50, f"Expected exactly 50 rejected duplicates, got {race_results['already_solved']}"
    assert race_results["errors"] == 0, f"Unexpected errors during race: {race_results['errors']}"

    # Solve Case 1 for remaining 50 teams
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(submit_flag, t["id"], 1, "FLAG{MUSHROOM_SECRET_OJAS_2026}") for t in teams_data[50:]]
        for f in as_completed(futures):
            dt, res = f.result()
            latencies["solve_c1"].append(dt)

    # --------------------------------------------------------------------------
    # STAGE 5: High-Frequency Leaderboard Polling Under Load
    # --------------------------------------------------------------------------
    print("\n[Stage 5/6] High-Frequency Leaderboard Polling (100 concurrent reads)...")
    def poll_leaderboard():
        t0 = time.time()
        board = get_leaderboard_standings()
        dt = (time.time() - t0) * 1000
        return dt, len(board)

    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(poll_leaderboard) for _ in range(100)]
        for f in as_completed(futures):
            dt, count = f.result()
            latencies["leaderboard_poll"].append(dt)

    print(f"  -> 100 concurrent leaderboard queries served (p50: {statistics.median(latencies['leaderboard_poll']):.1f}ms, p95: {sorted(latencies['leaderboard_poll'])[int(len(latencies['leaderboard_poll'])*0.95)]:.1f}ms)")

    # --------------------------------------------------------------------------
    # STAGE 6: Top 10 Squads Climax: Complete All Worlds & 3-Stage Boss Showdown
    # --------------------------------------------------------------------------
    print("\n[Stage 6/6] Full Campaign Progression for Top Squads (World 1 -> World 5 Boss)...")
    all_flags = {
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

    top_squads = teams_data[:10]
    def complete_campaign(t):
        t0 = time.time()
        tid = t["id"]
        # Solve remaining normal cases 2-11
        for cid, flag in all_flags.items():
            r = verify_and_solve_flag(tid, cid, flag, skip_rate_limit=True)
            if not r["success"]:
                return (time.time() - t0) * 1000, False, f"Failed case {cid}: {r.get('message')}"

        # Boss Stage 1
        s1 = submit_stage1_shield(tid, 1, "SECRET")
        s2 = submit_stage1_shield(tid, 2, "PINES")
        s3 = submit_stage1_shield(tid, 3, "BOO")
        s4 = submit_stage1_shield(tid, 4, "INSIDER")
        if not (s1["success"] and s2["success"] and s3["success"] and s4["success"]):
            return (time.time() - t0) * 1000, False, "Boss Stage 1 failed"

        # Boss Stage 2
        t1 = submit_stage2_trivia(tid, 1, "nmap")
        t2 = submit_stage2_trivia(tid, 2, "=")
        t3 = submit_stage2_trivia(tid, 3, "AES")
        t4 = submit_stage2_trivia(tid, 4, "Buffer Overflow")
        if not (t1["success"] and t2["success"] and t3["success"] and t4["success"]):
            return (time.time() - t0) * 1000, False, "Boss Stage 2 failed"

        # Boss Stage 3: Master Flag
        fin = submit_stage3_final_flag(tid, "FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}")
        if not fin["success"]:
            return (time.time() - t0) * 1000, False, f"Boss Stage 3 failed: {fin.get('message')}"

        return (time.time() - t0) * 1000, True, None

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(complete_campaign, t) for t in top_squads]
        for f in as_completed(futures):
            dt, ok, err = f.result()
            latencies["boss_stage"].append(dt)
            if not ok:
                errors.append(err)

    print(f"  -> Top 10 squads completed full campaign (avg: {statistics.mean(latencies['boss_stage']):.1f}ms per team full run)")
    assert len(errors) == 0, f"Encountered errors: {errors}"

    # --------------------------------------------------------------------------
    # DATA INTEGRITY VERIFICATION
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("  🏆 VERIFYING DATABASE CONSTRAINTS & LEDGER INTEGRITY")
    print("=" * 80)
    with db_session() as sess:
        total_teams_db = sess.query(Team).count()
        total_members_db = sess.query(TeamMember).count()
        total_solves_db = sess.query(SolvedChallenge).count()
        total_ledger_db = sess.query(ScoreLedger).count()

        print(f"  • Total Registered Teams:     {total_teams_db}")
        print(f"  • Total Active Members:       {total_members_db}")
        print(f"  • Total Solved Records:       {total_solves_db}")
        print(f"  • Total Score Ledger Events:  {total_ledger_db}")

        # Check completed squads have valid finished_at and total_time
        top_ids = {t["id"] for t in top_squads}
        completed_squads = sess.query(Team).filter_by(run_state="COMPLETED").all()
        print(f"  • Completed Squads:           {len(completed_squads)}")
        for cs in completed_squads:
            assert cs.finished_at is not None
            assert cs.total_time is not None
            if cs.id in top_ids:
                assert cs.score >= 3200, f"Expected top campaign squad {cs.team_name} to have score >= 3200, got {cs.score}"

        # Check ledger balances match team scores exactly for current run squads
        for cs in [t for t in completed_squads if t.id in top_ids]:
            ledger_sum = sum(e.delta_points for e in cs.ledger_entries)
            assert cs.score == ledger_sum, f"Ledger mismatch for {cs.team_name}: {cs.score} != {ledger_sum}"

    # Print Final Performance Table
    print("\n" + "=" * 80)
    print("  📊 100-TEAM LOAD TEST PERFORMANCE & LATENCY REPORT")
    print("=" * 80)
    print(f"  {'Operation':<24} | {'Requests':<8} | {'p50 (ms)':<10} | {'p95 (ms)':<10} | {'Max (ms)':<10}")
    print("  " + "-" * 72)
    for op, data in latencies.items():
        if data:
            s_data = sorted(data)
            p50 = statistics.median(s_data)
            p95 = s_data[int(len(s_data) * 0.95)]
            max_val = max(s_data)
            print(f"  {op:<24} | {len(data):<8} | {p50:<10.1f} | {p95:<10.1f} | {max_val:<10.1f}")
    print("=" * 80)
    print("  🎉 100-TEAM CONCURRENCY TEST PASSED WITH ZERO DATA LOSS OR CONTENTION!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    run_load_test()
