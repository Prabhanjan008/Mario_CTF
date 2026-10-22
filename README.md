# Mario: The Cyber Heist (OJAS CTF)

A retro Mario-themed cybersecurity Capture The Flag (CTF) web game built for Chanakya University's OJAS tech fest.

Students register as solo operatives, explore 5 worlds on an interactive 3D map, investigate 12 forensic and cybersecurity cases, and unlock the final boss vault to recover the Golden Star.

---

## How to Run Locally

### Requirements
* Python 3.10 or higher installed on your computer.

### Quick Start in 4 Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Prabhanjan008/Mario_CTF.git
   cd Mario_CTF
   ```

2. **Create and activate a virtual environment:**
   * On Windows:
     ```bash
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   * On Mac/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the game server:**
   ```bash
   python run_production.py
   ```
   Now open your browser and go to: `http://localhost:5000`

---

## Folder Guide (Where Everything Lives)

Here is a simple map of every folder and main file in the project:

```text
├── app.py                 # Starts the Flask app and registers all routes
├── run_production.py      # Starts the local server using Waitress
├── wsgi.py                # Connects the app to production servers (Gunicorn/Render)
├── requirements.txt       # List of Python packages needed to run the project
│
├── database/              # Everything related to storing game data
│   ├── game.db            # SQLite database file storing players, scores, and solves
│   ├── init_db.py         # Helper script to create and seed fresh tables
│   ├── schema.sql         # Raw SQL table definitions
│   └── seed_data.py       # Default list of all 5 worlds and 12 challenges
│
├── models/                # Python definitions of our database tables
│   ├── db.py              # Connects to the database and manages database sessions
│   ├── schema.py          # Table models: Team, Challenge, SolvedChallenge, etc.
│   ├── team.py            # Helpful database queries for player scores
│   └── challenge.py       # Helpful database queries for challenge states
│
├── routes/                # Handles web page URLs and API requests
│   ├── game.py            # Home page, player briefing, lobby, and 3D map screens
│   ├── challenges.py      # Individual challenge pages, hint unlocking, and flag checks
│   └── admin.py           # Secret host dashboard for organizers to manage the game
│
├── services/              # Pure Python logic behind the game
│   ├── admin_service.py   # Checks host password and allows score adjustments
│   ├── auth_service.py    # Player registration, login codes, and session security
│   ├── boss_service.py    # Logic for the final stage 12 boss fight
│   ├── challenge_service.py # Checks submitted flags and deducts coins for hints
│   ├── competition_service.py # Controls game states: lobby, active, paused, finished
│   ├── leaderboard_service.py # Ranks players by score and completion time
│   ├── progression_service.py # Unlocks worlds as players earn stars
│   └── run_service.py     # Tracks each player's stopwatch timer
│
├── static/                # Files sent directly to the browser
│   ├── css/               # Styling and color themes for the game
│   ├── js/                # 3D Three.js graphics, sound effects, and timers
│   └── vendor/            # Offline libraries (Three.js WebGL engine)
│
├── templates/             # HTML files that make up the web pages
│   ├── base.html          # Main layout shared across all pages
│   ├── index.html         # Title screen with the 3D island
│   ├── briefing.html      # Player registration and case briefing
│   ├── map.html           # 3D interactive world map
│   ├── challenge.html     # Challenge workbench where players solve puzzles
│   ├── boss.html          # Final fortress boss arena
│   ├── admin.html         # Host control room
│   └── leaderboard.html   # Live score ranking table
│
└── tests/                 # Automated tests to make sure everything works
    ├── conftest.py        # Runs tests in an isolated temp database
    ├── test_ctf_production.py # Tests for flags, scoring, and registration
    └── test_timer_accuracy.py # Tests for stopwatch accuracy
```

---

## The 5 Worlds & 12 Challenges

The tournament has 12 hands-on challenges split across 5 worlds:

| World | Name | Cases | Topic Covered |
| :---: | :--- | :---: | :--- |
| **1** | Mushroom Village | #1 - #2 | Inspecting HTML elements, basic Caesar/ROT13 ciphers |
| **2** | Dark Forest | #3 - #5 | Image steganography (LSB), EXIF camera metadata, hex packet streams |
| **3** | Haunted Mansion | #6 - #8 | Directory path traversal, IDOR API manipulation, JWT session forgery |
| **4** | Koopa HQ | #9 - #11 | Linux bash forensics, SIEM log correlation, SQL injection authentication bypass |
| **5** | Final Fortress | #12 (Boss) | 3-stage finale: sector overrides, cybersecurity trivia, and the master flag |

---

## How Scoring & Hints Work

* **Starting Balance:** Every player starts with **100 Cyber Coins**.
* **Rewards:** Solving a challenge earns **Points**, **Coins**, and **1 Star**.
* **Hints:** If stuck, players can spend coins to unlock up to two hints per challenge.
* **Unlocking Worlds:** Players must solve earlier cases to earn stars and unlock later worlds. Unlocking World 5 requires all 11 stars from Worlds 1 to 4.
* **Zero-Hint Maximum:** If a player solves all 12 cases without buying hints, they finish with **3,350 Points**, **12 Stars**, and **1,825 Coins**.

---

## Running Automated Tests

To run the automated test suite:

```bash
pytest tests/
```

All tests run against an isolated temporary database so live player data is never modified.

---

## Event Host & Organizer Controls

* **Host Dashboard:** Located at `/admin`.
* **Host Keys:** Enter an authorized host passkey (e.g. `OJAS-HOST-ALPHA-7701`) to access:
  * Live player scores and submission logs.
  * Score and coin adjustment tools.
  * Timer pause/resume controls.
  * Database factory reset (used right before launching the real event).
  * CSV/JSON leaderboard export.
* **Leaderboard Screen:** Located at `/leaderboard` (protected by host key so organizers can project it on the big screen).
