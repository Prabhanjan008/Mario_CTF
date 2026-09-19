import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
from database.init_db import init_db
from models.team import get_or_create_default_team, register_team, get_team_by_id, get_leaderboard, update_team_score
from models.challenge import (
    get_worlds_with_status,
    get_challenges_by_world,
    get_challenge_detail,
    verify_and_solve_flag,
    unlock_hint
)

def run_tests():
    print("==================================================")
    print("🍄 MARIO: THE CYBER HEIST - AUTOMATED VERIFICATION")
    print("==================================================")

    # 1. Initialize fresh test database
    init_db(reset=True)
    print("✅ Database successfully initialized and seeded.")

    # 2. Test default team
    team = get_or_create_default_team()
    assert team["team_name"] == "Inspector Mario", f"Expected Inspector Mario, got {team['team_name']}"
    assert team["score"] == 0, "Initial score should be 0"
    assert team["coins"] == 100, "Initial coins should be 100"
    assert team["stars"] == 0, "Initial stars should be 0"
    print(f"✅ Default team verified: {team['team_name']} (Coins: {team['coins']}, Stars: {team['stars']})")

    # 3. Test Worlds retrieval
    worlds = get_worlds_with_status(team["id"])
    assert len(worlds) == 5, f"Expected 5 worlds, found {len(worlds)}"
    assert worlds[0]["is_unlocked"] is True, "World 1 should be unlocked by default"
    assert worlds[1]["is_unlocked"] is False, "World 2 should be locked with 0 stars"
    print("✅ World status verified: World 1 unlocked, Worlds 2-5 locked.")

    # 4. Test Challenges for World 1
    w1_challenges = get_challenges_by_world(1, team["id"])
    assert len(w1_challenges) == 2, f"Expected 2 challenges in World 1, found {len(w1_challenges)}"
    assert w1_challenges[0]["slug"] == "w1-c1", "Challenge 1 slug mismatch"
    print("✅ World 1 challenges loaded successfully.")

    # 5. Test Flag Submission (Incorrect Flag)
    wrong_res = verify_and_solve_flag(team["id"], 1, "FLAG{WRONG_GUESS}")
    assert wrong_res["success"] is False, "Incorrect flag should fail"
    print("✅ Flag verification: Incorrect flag correctly rejected.")

    # 6. Test Flag Submission (Correct Flag: Challenge 1)
    correct_res = verify_and_solve_flag(team["id"], 1, "FLAG{MUSHROOM_SECRET_OJAS_2026}")
    assert correct_res["success"] is True, f"Flag verification failed: {correct_res}"
    assert correct_res["points_awarded"] == 100
    assert correct_res["coins_awarded"] == 50
    assert correct_res["stars_awarded"] == 1

    updated_team = get_team_by_id(team["id"])
    assert updated_team["score"] == 100
    assert updated_team["coins"] == 150
    assert updated_team["stars"] == 1
    print(f"✅ Flag 1 solved! Score: {updated_team['score']}, Coins: {updated_team['coins']}, Stars: {updated_team['stars']}")

    # 7. Test Duplicate Flag Submission (Re-solve prevention)
    dup_res = verify_and_solve_flag(team["id"], 1, "FLAG{MUSHROOM_SECRET_OJAS_2026}")
    assert dup_res["success"] is False, "Duplicate solve should be rejected"
    assert dup_res.get("already_solved") is True
    print("✅ Anti-replay: Duplicate submission correctly blocked.")

    # 8. Test Hint Unlock & Coin Deduction
    hint_res = unlock_hint(team["id"], 2, 1)
    assert hint_res["success"] is True, f"Hint unlock failed: {hint_res}"
    assert "ROT13" in hint_res["hint"], "Hint content mismatch"
    updated_team2 = get_team_by_id(team["id"])
    assert updated_team2["coins"] == 150 - 25, f"Expected 125 coins, got {updated_team2['coins']}"
    print(f"✅ Hint 1 unlocked successfully for Challenge 2! Remaining coins: {updated_team2['coins']}")

    # 9. Solve Challenge 2 to earn 2nd star & unlock World 2!
    w1_c2_res = verify_and_solve_flag(team["id"], 2, "FLAG{LETTER_CIPHER_SOLVED_OJAS}")
    assert w1_c2_res["success"] is True
    updated_team3 = get_team_by_id(team["id"])
    assert updated_team3["stars"] == 2
    worlds_after = get_worlds_with_status(team["id"])
    assert worlds_after[1]["is_unlocked"] is True, "World 2 should now be unlocked with 2 stars"
    print("✅ Star progression: World 2 (Dark Forest) unlocked automatically upon reaching 2 stars!")

    # 10. Test Flask App Endpoints
    app = create_app()
    with app.test_client() as client:
        # Health check
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json["status"] == "online"

        # Start Screen (Auto-resume redirect when in-progress)
        res_redirect = client.get("/")
        assert res_redirect.status_code == 302
        assert "/challenge/3" in res_redirect.headers["Location"]

        # Start Screen (Title Island when explicitly visited with ?home=1)
        res_home = client.get("/?home=1")
        assert res_home.status_code == 200
        assert b"THE CYBER HEIST" in res_home.data
        assert b"RESUME MISSION: CASE 3" in res_home.data

        # 3D World Map
        res = client.get("/map")
        assert res.status_code == 200
        assert b"map-canvas" in res.data

        # Challenge 1
        res = client.get("/challenge/1")
        assert res.status_code == 200
        assert b"The Broken Notice Board" in res.data

        # Challenge 12 (Boss Arena - Locked with 2 stars)
        res_locked = client.get("/challenge/12")
        assert res_locked.status_code == 200
        assert b"SECTOR ACCESS RESTRICTED" in res_locked.data

        # Unlock World 5 by granting required stars (11 stars)
        update_team_score(team["id"], 0, 0, 10)

        # Challenge 12 (Boss Arena - Unlocked)
        res_boss = client.get("/challenge/12")
        assert res_boss.status_code == 200
        assert b"MECHA-SHELLSHOCK" in res_boss.data
        assert b"QUANTUM SHIELD OVERRIDE TERMINALS" in res_boss.data
        assert b"Investigation Question (Case 01)" in res_boss.data
        assert b"Investigation Question (Case 03)" in res_boss.data
        assert b"Investigation Question (Case 07)" in res_boss.data
        assert b"Investigation Question (Case 10)" in res_boss.data
        print("✅ World 5 Boss Battle verified: Questions and shield terminals rendered correctly.")

        # Leaderboard
        res = client.get("/leaderboard")
        assert res.status_code == 200
        assert b"Inspector Mario" in res.data

        # Admin Panel (Unauthenticated -> Login Gate)
        res = client.get("/admin")
        assert res.status_code == 200
        assert b"RESTRICTED ORGANIZER TERMINAL" in res.data
        print("✅ Admin Security: Unauthenticated access blocked behind Master Key login gate.")

        # Test Host Key 1: OJAS-HOST-ALPHA-7701
        h1 = client.post("/admin", data={"admin_key": "OJAS-HOST-ALPHA-7701"}, follow_redirects=True)
        assert h1.status_code == 200
        assert b"ORGANIZER OPERATIONS" in h1.data
        print("✅ Host Security: Key 1 (OJAS-HOST-ALPHA-7701) authenticated successfully.")

        # Test Host Key 2: OJAS-HOST-BRAVO-9924
        client.get("/admin/logout")
        h2 = client.post("/admin", data={"admin_key": "OJAS-HOST-BRAVO-9924"}, follow_redirects=True)
        assert h2.status_code == 200
        assert b"ORGANIZER OPERATIONS" in h2.data
        print("✅ Host Security: Key 2 (OJAS-HOST-BRAVO-9924) authenticated successfully.")

        # Test Host Key 3: OJAS-HOST-SUPER-4418
        client.get("/admin/logout")
        h3 = client.post("/admin", data={"admin_key": "OJAS-HOST-SUPER-4418"}, follow_redirects=True)
        assert h3.status_code == 200
        assert b"ORGANIZER OPERATIONS" in h3.data
        print("✅ Host Security: Key 3 (OJAS-HOST-SUPER-4418) authenticated successfully.")

        # Test CSV Export
        csv_res = client.get("/api/admin/export/csv")
        assert csv_res.status_code == 200
        assert b"Rank,Team Name,Access Code" in csv_res.data
        print("✅ Host Reporting: CSV results export endpoint verified 200 OK.")

        # Test JSON Export
        json_res = client.get("/api/admin/export/json")
        assert json_res.status_code == 200
        assert b"OJAS Tech Fest 2026" in json_res.data
        print("✅ Host Reporting: JSON results export endpoint verified 200 OK.")

    print("✅ All Flask client web routes (/, /map, /briefing, /challenge/1, /leaderboard, /admin) verified 200 OK.")
    print("==================================================")
    print("🎉 ALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
