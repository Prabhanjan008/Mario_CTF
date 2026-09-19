-- Mario: The Cyber Heist - CTF Database Schema

CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT UNIQUE NOT NULL,
    access_code TEXT UNIQUE NOT NULL,
    score INTEGER DEFAULT 0,
    coins INTEGER DEFAULT 100,
    stars INTEGER DEFAULT 0,
    current_world INTEGER DEFAULT 1,
    started_at DATETIME DEFAULT NULL,
    finished_at DATETIME DEFAULT NULL,
    total_time TEXT DEFAULT NULL,
    last_challenge_id INTEGER DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS worlds (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    subtitle TEXT NOT NULL,
    description TEXT NOT NULL,
    theme_color TEXT NOT NULL,
    icon TEXT NOT NULL,
    required_stars INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY,
    world_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    points INTEGER NOT NULL,
    coins_reward INTEGER NOT NULL,
    star_reward INTEGER DEFAULT 1,
    description TEXT NOT NULL,
    forensic_brief TEXT NOT NULL,
    interactive_type TEXT NOT NULL, -- 'web_dom', 'cipher_stream', 'stego_viewer', 'exif_analyzer', 'network_proxy', 'directory_hunt', 'idor_api', 'jwt_forge', 'recon_file', 'log_siem', 'sqli_shell', 'boss_terminal'
    flag_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    hint_1 TEXT NOT NULL,
    hint_1_cost INTEGER DEFAULT 20,
    hint_2 TEXT NOT NULL,
    hint_2_cost INTEGER DEFAULT 40,
    FOREIGN KEY (world_id) REFERENCES worlds(id)
);

CREATE TABLE IF NOT EXISTS solved_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    challenge_id INTEGER NOT NULL,
    solved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    awarded_points INTEGER NOT NULL,
    awarded_coins INTEGER NOT NULL,
    awarded_stars INTEGER NOT NULL,
    UNIQUE(team_id, challenge_id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(id)
);

CREATE TABLE IF NOT EXISTS hints_unlocked (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    challenge_id INTEGER NOT NULL,
    hint_num INTEGER NOT NULL, -- 1 or 2
    cost_paid INTEGER NOT NULL,
    unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, challenge_id, hint_num),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(id)
);

CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    challenge_id INTEGER NOT NULL,
    flag_attempt TEXT NOT NULL,
    is_correct INTEGER NOT NULL,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
