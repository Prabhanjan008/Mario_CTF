# Mario: The Cyber Heist (OJAS 2026 CTF)

A production-grade, Mario-inspired cybersecurity Capture The Flag (CTF) platform built for university hackathons and competitive cyber competitions. Features an interactive Three.js 3D world map, 8-bit retro audio synthesis, digital forensic workbenches, and multi-team tournament orchestration.

---

## 🌟 Key Architecture & Features

* **Squad Architecture (100+ Teams):**
  * Crockford Base32 cryptographic squad access codes (e.g. `CYBER-W7KP-92RM`).
  * Real-time multi-member concurrency: all members share live solve states, star progression, and hint logs without race conditions.
  * Cross-team session isolation and IDOR protection.

* **Authoritative Tournament Lifecycle:**
  * **LOBBY Mode:** Registration open, pre-game briefing room, challenges locked.
  * **ACTIVE Mode:** Synchronous mission dispatch across all registered squads.
  * **PAUSED & ENDED Modes:** Freeze state, lock flag submissions, and freeze the official podium.

* **High-Precision Monotonic Competition Clock:**
  * Decoupled from client operating system clocks and timezone offsets.
  * Driven by a client monotonic `performance.now()` engine calibrated by server UTC timestamps.
  * Automatic drift compensation upon browser tab switching or device sleep.
  * Interactive 24-hour local clock toggle mode.

* **12 Multi-Disciplinary Cybersecurity Challenges:**
  * **World 1: Grassland Gateway (Digital Forensics & Recon)**
    * Case 01: Exif Metadata Extraction
    * Case 02: Network Packet Inspection (PCAP)
    * Case 03: Linux File Permissions & SUID Auditing
  * **World 2: Underground Caverns (Web Security & Cryptanalysis)**
    * Case 04: SQL Injection Authentication Bypass
    * Case 05: Cryptographic Hash Cracking & Rainbow Tables
    * Case 06: Cross-Site Scripting (XSS) Sanitization
  * **World 3: Haunted Forest (Binary & Reverse Engineering)**
    * Case 07: Python Bytecode Decompilation
    * Case 08: Memory Buffer Overflow Analysis
    * Case 09: Encrypted Firmware Strings Extraction
  * **World 4: Bowser's Fortress (Cloud, API & Boss Showdown)**
    * Case 10: JWT Secret Tampering
    * Case 11: Insecure AWS S3 Bucket Enumeration
    * Case 12: Three-Stage Boss Showdown (Sector Shields → Cyber Trivia → Master Flag)

* **Host Organizer Command Center (`/admin`):**
  * Protected by PBKDF2-SHA256 salted passkey.
  * Real-time squad adjustments (points, stars, coins).
  * Mission restart/reopen capabilities and RFC-4180 CSV leaderboard exports.
  * Tamper-evident immutable audit trail.

---

## 🚀 Quickstart

### Prerequisites
* Python 3.10+
* Virtual Environment tool (`venv`)

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Prabhanjan008/Mario_CTF.git
   cd Mario_CTF
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database schema and seed challenges:**
   ```bash
   python -c "from models.db import init_database; init_database(reset=False, seed=True)"
   ```

5. **Start the production server:**
   ```bash
   python run_production.py
   ```
   * Platform will be live at `http://127.0.0.1:5000`

---

## 🧪 Automated Testing

Run the full automated test suite covering authentication, IDOR isolation, rate limiting, progression thresholds, and precision timer accuracy:

```bash
pytest tests/ -v
```

---

## 📁 Repository Structure

```text
├── app.py                     # Flask application factory & middleware
├── run_production.py          # Production Waitress WSGI runner
├── wsgi.py                    # Gunicorn / generic WSGI entrypoint
├── models/
│   ├── db.py                  # Thread-safe scoped session factory
│   └── schema.py              # Declarative models & UTC ISO serializers
├── routes/
│   ├── game.py                # Gameplay, squad registration & navigation
│   ├── challenges.py          # Flag submission & hint unlocking
│   └── admin.py               # Host tournament dashboard
├── services/
│   ├── auth_service.py        # Squad access codes & CSRF verification
│   ├── challenge_service.py   # Flag hash validation & ledger scoring
│   ├── competition_service.py # Tournament state machine (Lobby/Active)
│   ├── run_service.py         # Authoritative mission clock & timer
│   ├── progression_service.py # Star thresholds & world gating
│   ├── boss_service.py        # Three-stage Bowser fortress progression
│   ├── leaderboard_service.py # Deterministic tie-breaking standings
│   └── admin_service.py       # Host management & audit logging
├── static/
│   ├── js/                    # WebGL Three.js world map, audio synth, timer
│   └── css/                   # Cyberpunk Mario theme stylesheet
├── templates/                 # Jinja2 responsive templates
└── tests/                     # Production test suite & load tests
```

---

## 🛡️ License
Built for Chanakya University Tech Fest (OJAS 2026).
