# 🍄 MARIO: THE CYBER HEIST — PROFESSIONAL SYSTEM FLOW & TECHNICAL ARCHITECTURE
**Event:** Chanakya University • OJAS Tech Fest 2026  
**Document Type:** Full Game System Flow, Architectural Blueprint & State Machine Specification  
**Target Audience:** Software Engineers, System Architects, Event Hosts, CTF Platform Developers  

---

## 🏛️ 1. High-Level Architectural Topology

The platform operates as a high-performance, client-server hybrid CTF application designed for LAN tech fests. It combines server-side authoritative state management (Python/Flask + SQLite) with an immersive, hardware-accelerated 3D client layer (Three.js WebGL + Web Audio API).

```mermaid
graph TD
    subgraph Client Layer [Browser / Client Workstation]
        UI[HUD & Cyber UI Controls]
        WebGL[Three.js 3D WebGL Canvas Engine]
        Audio[Web Audio API Chiptune Synthesizer]
        Workbench[Forensic Workbench Engines DOM / Stego / Hex / JWT / SQL]
    end

    subgraph Transport Layer [HTTP / REST Endpoints]
        HTTP_GET[Page Navigation & 3D Render Routes]
        HTTP_POST[Atomic State API Requests /submit-flag, /unlock-hint]
        SSE_ADMIN[Admin Telemetry & Live Export Stream]
    end

    subgraph Application Layer [Flask Application Server - port 5000]
        GameBP[routes.game - Session & Navigation Controller]
        ChallengeBP[routes.challenges - Flag Engine & Gatekeeper]
        AdminBP[routes.admin - Host Master Console & Telemetry]
        ContextEngine[app.context_processor - Dynamic Resume Engine]
    end

    subgraph Persistence Layer [SQLite Database - cyber_heist.db]
        DB_Teams[(teams: Identity, Score, Timer, Progression)]
        DB_Worlds[(worlds: Sector Thresholds & Locks)]
        DB_Challenges[(challenges: 12 Forensic Cases & Payloads)]
        DB_Solves[(solved_challenges: Idempotent Solve Records)]
        DB_Hints[(unlocked_hints: Hint Ledger & Coin Audit)]
        DB_Logs[(submission_logs: Security & Audit Stream)]
    end

    UI --> HTTP_GET
    Workbench --> HTTP_POST
    HTTP_GET --> GameBP
    HTTP_GET --> ChallengeBP
    HTTP_POST --> ChallengeBP
    AdminBP --> SSE_ADMIN

    GameBP --> ContextEngine
    ContextEngine --> DB_Teams
    ChallengeBP --> DB_Challenges
    ChallengeBP --> DB_Solves
    ChallengeBP --> DB_Teams
    ChallengeBP --> DB_Hints
    AdminBP --> DB_Logs
    AdminBP --> DB_Teams
```

---

## 🔄 2. End-to-End Player Lifecycle State Machine

The player's journey is governed by a strict, server-enforced state machine ensuring fairness, session persistence, and crash recovery.

```mermaid
stateDiagram-v2
    [*] --> Standby: Access Title (/) or Briefing (/briefing)
    note right of Standby
        State: SQUAD_REGISTERED
        Timer: ⏱️ 00:00:00 [STANDBY]
        Started: NULL
        Finished: NULL
    end note

    Standby --> Standby: Register New Squad or Switch Squad Code
    Standby --> OverworldMap: Navigate to /map
    
    OverworldMap --> World1_Case1: Launch Case 1 (/challenge/1)
    note right of World1_Case1
        TRIGGER: First Challenge Entry
        Action: start_team_timer(team_id)
        State: MISSION_ACTIVE
        Timer: ⏱️ HH:MM:SS [ACTIVE]
    end note

    World1_Case1 --> Case_Investigation: Inspect Source / Decode ROT-13
    Case_Investigation --> Submit_Flag: POST /api/submit-flag

    Submit_Flag --> Flag_Rejected: Incorrect Flag
    Flag_Rejected --> Case_Investigation: Hint Unlock (/api/unlock-hint) or Retry

    Submit_Flag --> Flag_Accepted: Valid Flag Match
    note right of Flag_Accepted
        Atomic Transaction:
        1. Insert into solved_challenges
        2. +Points, +Coins, +Stars
        3. Recalculate unlocked worlds
        4. Auto-update last_challenge_id
    end note

    Flag_Accepted --> OverworldMap: Next Sector Check
    OverworldMap --> World2: Requires 2 Stars ⭐
    World2 --> World3: Requires 5 Stars ⭐
    World3 --> World4: Requires 8 Stars ⭐
    World4 --> World5_Boss: Requires 11 Stars ⭐

    World5_Boss --> Boss_Stage1: 4 Sector Keycodes
    Boss_Stage1 --> Boss_Stage2: 4 Cybersecurity Trivia
    Boss_Stage2 --> Boss_Stage3: Master Flag (FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION})

    Boss_Stage3 --> Mission_Completed: Solve Verified
    note right of Mission_Completed
        Action: finish_team_timer(team_id)
        State: MISSION_LOCKED
        Timer: 🏆 Frozen Permanently
    end note

    Mission_Completed --> Victory_Ceremony: /victory (3D Cinematic)
    Mission_Completed --> Mission_Debrief: /end (12-Case Forensic Audit)
    Mission_Completed --> Leaderboard: /leaderboard (Rank & Time Recorded)
```

---

## ⏱️ 3. Precision CTF Timer Architecture

Unlike simple client-side JavaScript timers that reset on browser reload or cheat easily, the platform implements a **Hybrid Server-Authoritative Timer Engine**:

| Phase | Display Badge | Trigger Condition | Persistence Method |
| :--- | :--- | :--- | :--- |
| **Phase 1: STANDBY** | `⏱️ 00:00:00 [READY]` | Team registration, Briefing, World Map navigation before any challenge is opened. | `teams.started_at IS NULL` |
| **Phase 2: ACTIVE** | `⏱️ HH:MM:SS [ACTIVE]` | Player clicks into World 1 Case 1 (`/challenge/1`) or Case 2. | Server sets `started_at = NOW()`. Client calculates delta: `(Date.now() - started_at_ms)`. |
| **Phase 3: LOCKED** | `🏆 HH:MM:SS [COMPLETED]` | Final Boss (Case 12) defeated or team reaches 12 stars. | Server writes `finished_at = NOW()` and `total_time = HH:MM:SS`. Freezes client ticker permanently. |

### Crash & Reload Resiliency:
- If a browser crashes, the tab is refreshed, or the squad moves to a different PC, logging in with their squad `access_code` instantly recovers `started_at` from SQLite.
- The top HUD calculates the exact elapsed time without losing a single second.
- `app.context_processor` automatically detects where the squad left off and offers **[ RESUME INVESTIGATION ]** or auto-redirects from `/` to their active case.

---

## 🔒 4. Server-Side Security & Anti-Cheat Protocols

1. **Gatekeeping (World Star Thresholds):**
   - Direct URL tampering (e.g., trying to access `/challenge/11` or `/challenge/12` immediately) triggers server-side validation in `routes/challenges.py`.
   - If `team['stars'] < required_stars`, the server renders `locked.html` and blocks challenge payloads.
2. **Idempotent Solve Ledger:**
   - Database enforces `UNIQUE(team_id, challenge_id)` on `solved_challenges`.
   - Resubmitting a previously solved flag returns `already_solved: true` without awarding duplicate points, coins, or stars.
3. **Coin Economy Protection:**
   - Unlocking hints requires an atomic transaction checking `coins >= hint_cost` (25, 50, or 75 coins).
   - Once unlocked, hint contents are stored in `unlocked_hints` so re-viewing hints never charges the squad twice.
4. **Boss Stage Isolation & Anti-Skip:**
   - `/victory` route checks `stars >= 12` or `finished_at IS NOT NULL`. Unauthorized requests are redirected back to `/map`.
5. **Separation of Privileges:**
   - Admin routes (`/admin`, `/api/admin/*`) require server-side session authentication validated against 3 hardcoded host passkeys (`OJAS-HOST-ALPHA-7701`, `OJAS-HOST-BRAVO-9924`, `OJAS-HOST-SUPER-4418`).
   - Host keys are never exposed in player HTML templates or client JavaScript files.

---

## 🗄️ 5. Database Schema & Relational Flow

```
┌──────────────────────────────────────┐       ┌─────────────────────────────────────┐
│                TEAMS                 │       │               WORLDS                │
├──────────────────────────────────────┤       ├─────────────────────────────────────┤
│ id (PK, INTEGER)                     │       │ id (PK, INTEGER)                    │
│ team_name (TEXT, UNIQUE)             │       │ name (TEXT)                         │
│ access_code (TEXT, UNIQUE)           │       │ slug (TEXT)                         │
│ score (INTEGER)                      │       │ description (TEXT)                  │
│ coins (INTEGER)                      │       │ required_stars (INTEGER)            │
│ stars (INTEGER)                      │       │ icon (TEXT)                         │
│ current_world (INTEGER)              │       │ order_index (INTEGER)               │
│ last_challenge_id (INTEGER)          │       └──────────────────┬──────────────────┘
│ started_at (TEXT)                    │                          │ 1:N
│ finished_at (TEXT)                   │                          ▼
│ total_time (TEXT)                    │       ┌─────────────────────────────────────┐
│ last_active (TEXT)                   │       │             CHALLENGES              │
└──────────────┬───────────────────────┘       ├─────────────────────────────────────┤
               │                               │ id (PK, INTEGER)                    │
               │ 1:N                           │ world_id (FK -> worlds.id)          │
               ├──────────────────────┐        │ title (TEXT)                        │
               ▼                      ▼        │ slug (TEXT)                         │
┌──────────────────────────┐ ┌──────────────────────┐ difficulty (TEXT)              │
│    SOLVED_CHALLENGES     │ │    UNLOCKED_HINTS    │ points (INTEGER)                │
├──────────────────────────┤ ├──────────────────────┤ coins_reward (INTEGER)          │
│ id (PK, INTEGER)         │ │ id (PK, INTEGER)     │ star_reward (INTEGER)           │
│ team_id (FK -> teams.id) │ │ team_id (FK)         │ flag (TEXT)                     │
│ challenge_id (FK)        │ │ challenge_id (FK)    │ interactive_type (TEXT)         │
│ solved_at (TEXT)         │ │ hint_number (INTEGER)│ hint1 / hint2 / hint3 (TEXT)    │
│ points_awarded (INTEGER) │ │ unlocked_at (TEXT)   └──────────────────┬──────────────┘
└──────────────────────────┘ └──────────────────────┘                  │
               │                                                       │
               └───────────────────────┬───────────────────────────────┘
                                       ▼
                       ┌───────────────────────────────┐
                       │        SUBMISSION_LOGS        │
                       ├───────────────────────────────┤
                       │ id (PK, INTEGER)              │
                       │ team_id (FK -> teams.id)      │
                       │ challenge_id (FK)             │
                       │ submitted_flag (TEXT)         │
                       │ is_correct (BOOLEAN)          │
                       │ ip_address (TEXT)             │
                       │ submitted_at (TEXT)           │
                       └───────────────────────────────┘
```

---

## 📊 6. Master Challenge Progression Matrix

| World | Sector Name | Case # | Case Title | Technical Category | Reward | Unlock Req |
| :---: | :--- | :---: | :--- | :--- | :--- | :---: |
| **W1** | Mushroom Village | **01** | The Broken Notice Board | Web Forensics (DOM) | 100 PTS / 50 🪙 / 1 ⭐ | 0 ⭐ |
| **W1** | Mushroom Village | **02** | The Suspicious Intercept | Cryptography (ROT-13) | 150 PTS / 75 🪙 / 1 ⭐ | 0 ⭐ |
| **W2** | Dark Forest | **03** | Deep Glitch in the Pines | Steganography (LSB Bitplane) | 200 PTS / 100 🪙 / 1 ⭐ | 2 ⭐ |
| **W2** | Dark Forest | **04** | The Shadow Metadata Trail | OSINT & Forensics (EXIF) | 200 PTS / 100 🪙 / 1 ⭐ | 2 ⭐ |
| **W2** | Dark Forest | **05** | Corrupted Proxy Stream | Network Forensics (Hex) | 250 PTS / 125 🪙 / 1 ⭐ | 2 ⭐ |
| **W3** | Haunted Mansion | **06** | Phantom Directory Traversal | Web Security (Path Traversal) | 250 PTS / 125 🪙 / 1 ⭐ | 5 ⭐ |
| **W3** | Haunted Mansion | **07** | Boo's Vault IDOR Manipulation | API Security (IDOR Bypass) | 300 PTS / 150 🪙 / 1 ⭐ | 5 ⭐ |
| **W3** | Haunted Mansion | **08** | Poltergeist Session Forgery | Auth Exploitation (JWT None) | 300 PTS / 150 🪙 / 1 ⭐ | 5 ⭐ |
| **W4** | Koopa HQ | **09** | The Framed Shellshock | Incident Recon (Reverse Shell) | 350 PTS / 175 🪙 / 1 ⭐ | 8 ⭐ |
| **W4** | Koopa HQ | **10** | Correlated SIEM Logs | Threat Hunting (SIEM Analysis) | 350 PTS / 175 🪙 / 1 ⭐ | 8 ⭐ |
| **W4** | Koopa HQ | **11** | Koopa Fortress SQLi Console | Database Security (SQL Injection) | 400 PTS / 200 🪙 / 1 ⭐ | 8 ⭐ |
| **W5** | Final Fortress | **12** | Mecha-Shellshock Showdown | 3D Arena & Cyber Synthesis | 500 PTS / 250 🪙 / 1 ⭐ | 11 ⭐ |

---

## 🎛️ 7. Administrative Oversight & Live Telemetry Flow

```mermaid
sequenceDiagram
    autonumber
    actor Host as Event Organizer
    participant AdminUI as Host Portal (/admin)
    participant AdminRoute as routes.admin
    participant DB as SQLite DB
    actor Player as Competitor Squad

    Player->>DB: Submits Flag (/api/submit-flag)
    DB-->>AdminRoute: Logged into submission_logs table
    Host->>AdminUI: Authenticates with Host Master Passkey
    AdminUI->>AdminRoute: POST /admin/login (Verify Passkey)
    AdminRoute-->>AdminUI: Session Token Granted
    AdminUI->>AdminRoute: GET /api/admin/overview
    AdminRoute->>DB: Fetch aggregate team scores, solve counts & audit stream
    DB-->>AdminUI: Render real-time leaderboard, activity feed & timers
    Host->>AdminUI: Click "Export Standings (CSV)"
    AdminUI->>AdminRoute: GET /api/admin/export/csv
    AdminRoute-->>Host: Generates RFC-4180 compliant CSV file
```

---

## ⚡ 8. Summary of Key Architectural Strengths

1. **Zero External Asset Dependencies:** Three.js and all chiptune audio operate purely locally; no external CDNs or cloud storage required for offline campus LAN events.
2. **Deterministic State Synchronization:** SQLite WAL mode ensures concurrent team flag submissions are processed atomically without race conditions.
3. **Fail-Safe Resume Protocol:** Teams can close laptops, switch browsers, or experience power cuts; reconnecting with their squad code resumes exact case state with zero progress loss.
4. **Comprehensive Audit Trail:** Organizers possess full forensic visibility over all submission timestamps, IP origins, and hint purchases.
