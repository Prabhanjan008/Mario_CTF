import os
import sqlite3
import hashlib
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "game.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def hash_flag(flag: str, salt: str) -> str:
    cleaned = flag.strip()
    return hashlib.sha256(f"{cleaned}:{salt}".encode("utf-8")).hexdigest()

def init_db(reset: bool = False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    if reset:
        cursor.execute("DELETE FROM submissions")
        cursor.execute("DELETE FROM solved_challenges")
        cursor.execute("DELETE FROM hints_unlocked")
        cursor.execute("DELETE FROM audit_logs")
        cursor.execute("DELETE FROM teams")
        try:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('teams', 'submissions', 'solved_challenges', 'hints_unlocked', 'audit_logs')")
        except sqlite3.OperationalError:
            pass

    # Seed Worlds
    worlds = [
        (1, "Mushroom Village", "Sector 01: Ground Zero", "The perimeter of the Mushroom Kingdom. Security cameras caught anomalous spikes before the golden vault went dark.", "#39ff14", "🍄", 0, 1),
        (2, "Dark Forest", "Sector 02: Digital Woods", "A dense encrypted forest of proxy hops and covert communication relays used by the rogue syndicate.", "#00e5ff", "🌲", 2, 1),
        (3, "Haunted Mansion", "Sector 03: Phantom Network", "An abandoned web mainframe haunted by broken authentication protocols, ghost tokens, and hidden corridors.", "#bf00ff", "👻", 5, 1),
        (4, "Koopa HQ", "Sector 04: Industrial Bastion", "A fortified server bunker run by Shellshock. Hardened defenses, SIEM alerts, and deep administrative archives.", "#ff3131", "🐢", 8, 1),
        (5, "Final Fortress", "Sector 05: Master Vault", "The cyber citadel where the Golden Star is locked behind an active quantum energy shield guarded by Mecha-Shellshock.", "#ffe600", "🏰", 11, 1),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO worlds (id, name, subtitle, description, theme_color, icon, required_stars, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, worlds)

    # Seed Challenges
    raw_challenges = [
        # World 1
        (
            1, 1, "The Broken Notice Board", "w1-c1", "Web Forensics", "Easy", 100, 50, 1,
            "The town digital bulletin board has been corrupted by the infiltrator. Strange glitched characters are flickering on the screen, hiding crucial forensic clues inside the DOM and network response.",
            "INVESTIGATION BRIEF: Examine the inspector DOM tree and network packet capture from the village board terminal. Look for hidden data attributes and commented payload packets.",
            "web_dom",
            "FLAG{MUSHROOM_SECRET_OJAS_2026}",
            "Check HTML inspect element comments and data-payload tags embedded in the broken board.", 20,
            "Look for a base64 encoded token inside the CSS style comment labeled 'cyber-heist-token'.", 40
        ),
        (
            2, 1, "The Suspicious Intercept", "w1-c2", "Cryptography", "Easy", 150, 75, 1,
            "Forensics officers recovered a dropped data slate containing an encrypted transmission sent moments after the vault breach. It contains a multi-layered obfuscation string.",
            "INVESTIGATION BRIEF: Intercepted transmission: 'SYNT{YRGGRE_PVCURE_FBYIRQ_BWNF}'. The perpetrator applied a classic Caesar rotation cipher commonly utilized in low-level cyber syndicates.",
            "cipher_stream",
            "FLAG{LETTER_CIPHER_SOLVED_OJAS}",
            "Notice how the string starts with 'SYNT' instead of 'FLAG'. Try ROT13 rotation.", 25,
            "Apply Caesar shift 13: S->F, Y->L, N->A, T->G. Decode the entire string into uppercase.", 45
        ),

        # World 2
        (
            3, 2, "Deep Glitch in the Pines", "w2-c1", "Steganography", "Medium", 200, 100, 1,
            "A surveillance drone over Sector 02 captured a high-resolution holographic snapshot of the pine ridge. Thermal and bitplane analysis shows pixel disparities.",
            "INVESTIGATION BRIEF: The drone image contains hidden information encoded inside the Least Significant Bit (LSB) channel of the RGB matrix. Extract the concealed ASCII payload.",
            "stego_viewer",
            "FLAG{FOREST_PIXEL_STEGO_OJAS}",
            "Switch the steganography visualizer to LSB Green & Blue planes to see the secret layer.", 30,
            "The red plane reveals hexadecimal offsets. Combined with LSB bits, the ASCII text reads: FLAG{FOREST_PIXEL_STEGO_OJAS}.", 60
        ),
        (
            4, 2, "The Shadow Metadata Trail", "w2-c2", "OSINT & Forensics", "Medium", 200, 100, 1,
            "A rogue camera file was left in the digital undergrowth. The perpetrator stripped visible timestamps, but left raw EXIF camera metadata intact.",
            "INVESTIGATION BRIEF: Inspect the metadata headers of 'evidence_pine_drone.raw'. Find the creator software, GPS coordinate tag, and the confidential Operator Notes field.",
            "exif_analyzer",
            "FLAG{METADATA_TRAIL_REVEALED_OJAS}",
            "Check the 'ImageDescription' and 'UserComment' EXIF tag fields using the metadata terminal.", 30,
            "The UserComment tag holds base64 data. Decoded value reveals the secret checkpoint flag.", 60
        ),
        (
            5, 2, "Corrupted Proxy Stream", "w2-c3", "Network Forensics", "Medium", 250, 125, 1,
            "Our sensor towers captured an unencrypted Wi-Fi beacon burst passing through the forest relay. The transmission is serialized in raw hexadecimal bytes.",
            "INVESTIGATION BRIEF: Hex dump recovered: '464c41477b4441524b5f464f524553545f53545245414d5f4445434f4445447d'. Convert the network octets back to ASCII strings.",
            "network_proxy",
            "FLAG{DARK_FOREST_STREAM_DECODED}",
            "Each pair of hex characters represents an ASCII character. 46 = 'F', 4C = 'L', 41 = 'A'...", 35,
            "Run hex to ASCII conversion on the entire string to reconstruct the complete packet.", 65
        ),

        # World 3
        (
            6, 3, "Phantom Directory Traversal", "w3-c1", "Web Security", "Medium", 250, 125, 1,
            "The Haunted Mansion hosts a spooky old web server running an outdated file viewer service. The parameter `file=welcome.txt` handles content loading.",
            "INVESTIGATION BRIEF: Probe the server path traversal vulnerabilities using relative path sequences (`../../`) or inspect `/robots.txt` and `/.git/HEAD` to locate the concealed archive.",
            "directory_hunt",
            "FLAG{BOO_GHOST_PATH_DISCOVERED}",
            "Check the server's `/robots.txt` configuration to see which directories are disallowed from web crawlers.", 35,
            "Navigating to the restricted `/secret_attic/ghost_manifesto.bak` unlocks the directory flag.", 65
        ),
        (
            7, 3, "Boo's Vault IDOR Manipulation", "w3-c2", "API Security", "Hard", 300, 150, 1,
            "The Boo syndicate maintains an internal storage locker API at `/api/v1/vault?locker_id=1042`. As guest inspector, your ID is 1042. But what about VIP Locker 0001?",
            "INVESTIGATION BRIEF: Test Insecure Direct Object References (IDOR) by intercepting and adjusting the query parameters and headers sent to the locker endpoint.",
            "idor_api",
            "FLAG{API_AUTH_BYPASS_OJAS}",
            "Inspect the API call in your developer tools. What happens if you request `locker_id=1` or `locker_id=0`?", 40,
            "Set `locker_id=1` with header `X-Access-Level: master_phantom` to unlock King Boo's private safe.", 75
        ),
        (
            8, 3, "Poltergeist Session Forgery", "w3-c3", "Token Exploitation", "Hard", 300, 150, 1,
            "Access to the mansion control room requires a valid JSON Web Token (JWT). The issued cookie `session_token` marks your role as `guest`. The algorithm is configured insecurely to 'none'.",
            "INVESTIGATION BRIEF: Deconstruct the base64url header and payload of the JWT. Modify `\"role\": \"guest\"` to `\"role\": \"admin\"` and switch `\"alg\": \"none\"` to forge master access.",
            "jwt_forge",
            "FLAG{SESSION_FORGERY_DETECTED_OJAS}",
            "JWT structure consists of Header.Payload.Signature. The server accepts `alg: none`.", 45,
            "Craft payload `{\"role\": \"admin\", \"realm\": \"haunted_mansion\", \"user\": \"inspector\"}` and strip the signature.", 80
        ),

        # World 4
        (
            9, 4, "The Framed Shellshock Recon", "w4-c1", "Forensics", "Hard", 350, 175, 1,
            "Initial intelligence blamed Koopa commander Shellshock for the heist. However, his private server was breached 48 hours prior to the theft. Someone planted false footprints!",
            "INVESTIGATION BRIEF: Analyze the system modification history and timestamp anomalies in Shellshock's bash profile to identify the real infiltrator's IP subnet.",
            "recon_file",
            "FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}",
            "Compare the file creation dates against the time the golden star was stolen. Notice the time difference.", 50,
            "Look for an injected reverse shell command inside the hidden file `.bash_logout.bak`.", 85
        ),
        (
            10, 4, "Correlated SIEM Log Breaches", "w4-c2", "Threat Hunting", "Hard", 350, 175, 1,
            "The Koopa fortress centralized SIEM log repository recorded 50,000 requests during the blackout. One continuous session generated unusual 401s followed by a 200 OK via backdoor.",
            "INVESTIGATION BRIEF: Filter security logs for successful administrative logins originating from unauthorized internal gateway IP `10.99.13.37`.",
            "log_siem",
            "FLAG{CORRELATED_LOGS_INSIDER_OJAS}",
            "Filter queries for IP `10.99.13.37` and status code `200` on route `/internal/admin/override`.", 50,
            "The user-agent header contains an obfuscated insider token that decodes to the flag.", 85
        ),
        (
            11, 4, "Koopa Fortress Mainframe Bypass", "w4-c3", "SQL Injection", "Hard", 400, 200, 1,
            "To gain entry into the citadel transit elevator, you must query the Koopa Personnel Database. The login form executes an unsanitized query string.",
            "INVESTIGATION BRIEF: Exploit SQL injection on the personnel search field: `SELECT * FROM officers WHERE badge_id = 'INPUT'`. Force the query to evaluate to true or union select confidential secrets.",
            "sqli_shell",
            "FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}",
            "Try submitting standard SQL tautology: `' OR '1'='1` in the badge ID field.", 60,
            "Use `' UNION SELECT 1, flag, 3, 4 FROM vault_secrets --` to dump the hidden vault secrets table.", 90
        ),

        # World 5
        (
            12, 5, "Master Key Synthesis: The Mecha-Shellshock Showdown", "w5-c1", "Master Synthesis", "Expert", 500, 300, 2,
            "You have penetrated the core vault of the Final Fortress. Standing between you and the stolen Golden Star is Mecha-Shellshock, powered by the rogue Cyber Warden AI.",
            "INVESTIGATION BRIEF: Enter the master sequence overrides gathered across all 4 previous sectors: Sector 1 Hash, Sector 2 Relay, Sector 3 Ghost Key, and Sector 4 Insider Trace. Lower the quantum shields and recover the Golden Star!",
            "boss_terminal",
            "FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}",
            "The 4 override codes correspond to the key phrases solved in previous worlds: SECRET, PINES, BOO, INSIDER.", 70,
            "Combine all 4 override hashes in sequence to trigger shield shutdown: OVERRIDE-OJAS-ALPHA-OMEGA.", 120
        ),
    ]

    for item in raw_challenges:
        (
            c_id, world_id, title, slug, category, difficulty, points, coins, stars,
            description, brief, itype, raw_flag, h1, h1_cost, h2, h2_cost
        ) = item

        salt = uuid.uuid4().hex[:16]
        f_hash = hash_flag(raw_flag, salt)

        cursor.execute("""
            INSERT OR REPLACE INTO challenges (
                id, world_id, title, slug, category, difficulty, points, coins_reward, star_reward,
                description, forensic_brief, interactive_type, flag_hash, salt, hint_1, hint_1_cost, hint_2, hint_2_cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c_id, world_id, title, slug, category, difficulty, points, coins, stars,
            description, brief, itype, f_hash, salt, h1, h1_cost, h2, h2_cost
        ))

    # Create default starter team if not exists
    cursor.execute("SELECT id FROM teams WHERE team_name = 'Inspector Mario'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO teams (team_name, access_code, score, coins, stars, current_world)
            VALUES ('Inspector Mario', 'MARIO-OJAS-2026', 0, 100, 0, 1)
        """)

    conn.commit()
    conn.close()
    print("Database initialized successfully with 5 Worlds and 12 CTF Challenges.")

if __name__ == "__main__":
    init_db(reset=True)
