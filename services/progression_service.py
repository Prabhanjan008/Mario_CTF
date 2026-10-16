"""
Game Progression Service for Mario: The Cyber Heist.
Enforces world unlock thresholds, normal stars calculation (Cases 1-11),
and challenge availability server-side.
"""

from models.db import db_session
from models.schema import World, Challenge, SolvedChallenge, HintUnlocked, Team

NORMAL_CHALLENGE_IDS = list(range(1, 12))  # Cases 1 through 11
BOSS_CHALLENGE_ID = 12                     # World 5 Boss Showdown
BOSS_REQUIRED_STARS = 11                   # 11 normal cases required for Boss


def calculate_normal_stars(team_id: int, sess=None) -> int:
    """
    Derives normal-case stars directly from valid solve records (Cases 1 to 11).
    Honors team.stars if manually set higher by administrator.
    """
    if sess is None:
        with db_session() as s:
            return calculate_normal_stars(team_id, s)

    count = (
        sess.query(SolvedChallenge)
        .filter(
            SolvedChallenge.team_id == team_id,
            SolvedChallenge.challenge_id.in_(NORMAL_CHALLENGE_IDS)
        )
        .count()
    )
    team = sess.query(Team).filter_by(id=team_id).first()
    if team and team.stars is not None and team.stars > count:
        return team.stars
    return count


def get_worlds_with_status(team_id: int) -> list:
    """
    Returns all 5 worlds with real-time unlock status, completed status,
    and solve telemetry derived from the database.
    """
    with db_session() as sess:
        worlds = sess.query(World).order_by(World.id.asc()).all()
        normal_stars = calculate_normal_stars(team_id, sess)

        # Get solved challenge IDs for this team
        solves = sess.query(SolvedChallenge.challenge_id).filter_by(team_id=team_id).all()
        solved_ids = {s[0] for s in solves}

        results = []
        for w in worlds:
            w_dict = w.to_dict()
            w_challenges = sess.query(Challenge.id).filter_by(world_id=w.id).all()
            w_c_ids = [c[0] for c in w_challenges]

            solved_in_w = sum(1 for cid in w_c_ids if cid in solved_ids)
            total_in_w = len(w_c_ids)

            w_dict["solved_count"] = solved_in_w
            w_dict["total_challenges"] = total_in_w
            w_dict["is_unlocked"] = (normal_stars >= w.required_stars)
            w_dict["is_completed"] = (solved_in_w > 0 and solved_in_w == total_in_w)
            w_dict["team_stars"] = normal_stars
            results.append(w_dict)

        return results


def is_challenge_unlocked(team_id: int, challenge_id: int) -> tuple[bool, str, int]:
    """
    Validates whether a specific challenge is unlocked for the team.
    Returns (is_unlocked, reason_message, required_stars).
    """
    with db_session() as sess:
        challenge = sess.query(Challenge).filter_by(id=challenge_id).first()
        if not challenge:
            return False, "Challenge does not exist.", 0

        world = sess.query(World).filter_by(id=challenge.world_id).first()
        if not world:
            return False, "Sector does not exist.", 0

        normal_stars = calculate_normal_stars(team_id, sess)

        if challenge_id == BOSS_CHALLENGE_ID:
            if normal_stars < BOSS_REQUIRED_STARS:
                return (
                    False,
                    f"Final Fortress is sealed by Quantum Shielding! You need all 11 Sector Stars to breach the vault (Current: {normal_stars}/11 ⭐).",
                    BOSS_REQUIRED_STARS
                )
            return True, "Final Fortress Vault Breached!", BOSS_REQUIRED_STARS

        if normal_stars < world.required_stars:
            return (
                False,
                f"Sector {world.name} is locked! Requires {world.required_stars} ⭐ (Current: {normal_stars} ⭐).",
                world.required_stars
            )

        return True, "Unlocked", world.required_stars


def get_challenges_by_world(world_id: int, team_id: int) -> list:
    """Fetches challenges for a world with solved flags masked and status."""
    with db_session() as sess:
        challenges = sess.query(Challenge).filter_by(world_id=world_id).order_by(Challenge.id.asc()).all()
        solves = {s.challenge_id for s in sess.query(SolvedChallenge).filter_by(team_id=team_id).all()}
        unlocked_hints = (
            sess.query(HintUnlocked.challenge_id, HintUnlocked.hint_num)
            .filter_by(team_id=team_id)
            .all()
        )
        hint_map = {}
        for c_id, h_num in unlocked_hints:
            hint_map.setdefault(c_id, []).append(h_num)

        out = []
        for c in challenges:
            c_dict = c.to_dict(mask_hints=True, mask_secrets=True)
            c_dict["is_solved"] = c.id in solves
            c_dict["hints_unlocked"] = hint_map.get(c.id, [])
            out.append(c_dict)

        return out


def get_challenge_detail(challenge_id: int, team_id: int) -> dict:
    """
    Returns full challenge detail, masking un-purchased hints and raw secrets.
    Computes prev/next navigation links based on current star progression.
    """
    with db_session() as sess:
        challenge = sess.query(Challenge).filter_by(id=challenge_id).first()
        if not challenge:
            return None

        world = sess.query(World).filter_by(id=challenge.world_id).first()
        normal_stars = calculate_normal_stars(team_id, sess)

        is_solved = (
            sess.query(SolvedChallenge)
            .filter_by(team_id=team_id, challenge_id=challenge_id)
            .first() is not None
        )

        unlocked_hints = {
            h.hint_num
            for h in sess.query(HintUnlocked).filter_by(team_id=team_id, challenge_id=challenge_id).all()
        }

        c_dict = challenge.to_dict(mask_hints=True, mask_secrets=True)
        c_dict["world"] = world.to_dict() if world else None
        c_dict["is_solved"] = is_solved
        c_dict["hints_unlocked"] = list(unlocked_hints)

        # Reveal only unlocked hints
        c_dict["hint_1"] = challenge.hint_1 if 1 in unlocked_hints else None
        c_dict["hint_2"] = challenge.hint_2 if 2 in unlocked_hints else None

        # Fetch sibling challenges in this world
        w_challenges = (
            sess.query(Challenge)
            .filter_by(world_id=challenge.world_id)
            .order_by(Challenge.id.asc())
            .all()
        )
        team_solves = {
            s.challenge_id
            for s in sess.query(SolvedChallenge).filter_by(team_id=team_id).all()
        }

        w_list = []
        for ch in w_challenges:
            w_list.append({
                "id": ch.id,
                "title": ch.title,
                "points": ch.points,
                "coins_reward": ch.coins_reward,
                "star_reward": ch.star_reward,
                "interactive_type": ch.interactive_type,
                "is_solved": ch.id in team_solves
            })
        c_dict["world_challenges"] = w_list

        # Navigation: Prev / Next
        c_ids = [ch["id"] for ch in w_list]
        cur_idx = c_ids.index(challenge_id) if challenge_id in c_ids else -1

        c_dict["prev_challenge_id"] = c_ids[cur_idx - 1] if cur_idx > 0 else None

        if cur_idx >= 0 and cur_idx < len(c_ids) - 1:
            c_dict["next_challenge_id"] = c_ids[cur_idx + 1]
            c_dict["next_challenge_title"] = w_list[cur_idx + 1]["title"]
        else:
            # Check if next world is unlocked
            next_w = sess.query(World).filter_by(id=challenge.world_id + 1).first()
            if next_w and normal_stars >= next_w.required_stars:
                nxt_c = (
                    sess.query(Challenge)
                    .filter_by(world_id=next_w.id)
                    .order_by(Challenge.id.asc())
                    .first()
                )
                c_dict["next_challenge_id"] = nxt_c.id if nxt_c else None
                c_dict["next_challenge_title"] = f"{next_w.name}: {nxt_c.title}" if nxt_c else None
            else:
                c_dict["next_challenge_id"] = None
                c_dict["next_challenge_title"] = None

        return c_dict
