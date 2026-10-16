# 🍄 MARIO: THE CYBER HEIST — CTF OVERVIEW & COMPLETE WALKTHROUGH
**Event:** Chanakya University • OJAS Tech Fest 2026  
**Document:** Official Challenge Guide & Solution Walkthrough  

---

## 🕹️ 1. Platform Overview & Game Mechanics

**Mario: The Cyber Heist** is an interactive, story-driven cybersecurity Capture-the-Flag (CTF) platform designed for OJAS Tech Fest 2026. Players step into the role of digital forensic investigators assisting Inspector Mario to retrieve the stolen Golden Star and stop Mecha-Shellshock.

### Core Progression Mechanics:
- **⭐ Stars:** Earned by solving challenges. Star milestones automatically unlock subsequent sectors:
  - **World 1 (Mushroom Village):** Available immediately (0 ⭐)
  - **World 2 (Dark Forest):** Unlocks at **2 ⭐**
  - **World 3 (Haunted Mansion):** Unlocks at **5 ⭐**
  - **World 4 (Koopa HQ):** Unlocks at **8 ⭐**
  - **World 5 (Final Fortress):** Unlocks at **11 ⭐**
- **🪙 Coins:** Awarded for successful flag submissions. Coins can be spent in the in-game hint terminal to purchase progressive clues without impacting total score.
- **🗺️ Interactive 3D World Map (`/map`):** Built with Three.js WebGL to dynamically visualize unlocked sectors and case locations.
- **🏆 Live Leaderboard (`/leaderboard`):** Real-time rank, score, stars, and solve counts for participating squads.
- **🔐 Host / Admin Center (`/admin`):** Monitoring dashboard for event organizers showing real-time solves, submission logs, and exportable reports.

---

## 🗺️ 2. Sector Hierarchy & Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│ WORLD 1: MUSHROOM VILLAGE (Web Forensics & Cryptography)               │
│ Case 1: The Broken Notice Board  ──► FLAG{MUSHROOM_SECRET_OJAS_2026}   │
│ Case 2: The Suspicious Intercept ──► FLAG{LETTER_CIPHER_SOLVED_OJAS}   │
├────────────────────────────────────────────────────────────────────────┤
│ WORLD 2: DARK FOREST (Stego, OSINT Metadata, Hex Streams) [Req: 2 ⭐]   │
│ Case 3: Deep Glitch in Pines     ──► FLAG{FOREST_PIXEL_STEGO_OJAS}     │
│ Case 4: The Shadow Metadata Trail──► FLAG{METADATA_TRAIL_REVEALED_OJAS}│
│ Case 5: Corrupted Proxy Stream   ──► FLAG{DARK_FOREST_STREAM_DECODED} │
├────────────────────────────────────────────────────────────────────────┤
│ WORLD 3: HAUNTED MANSION (Directory Traversal, IDOR, JWT) [Req: 5 ⭐]  │
│ Case 6: Phantom Directory Hunt   ──► FLAG{BOO_GHOST_PATH_DISCOVERED}   │
│ Case 7: Boo's Vault IDOR API     ──► FLAG{API_AUTH_BYPASS_OJAS}        │
│ Case 8: Poltergeist JWT Forgery  ──► FLAG{SESSION_FORGERY_DETECTED_OJAS}│
├────────────────────────────────────────────────────────────────────────┤
│ WORLD 4: KOOPA HQ (Bash Forensics, SIEM Logs, SQL Injection) [Req: 8 ⭐]│
│ Case 9: The Framed Shellshock    ──► FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}  │
│ Case 10: Correlated SIEM Logs    ──► FLAG{CORRELATED_LOGS_INSIDER_OJAS}│
│ Case 11: Koopa Fortress SQLi     ──► FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}  │
├────────────────────────────────────────────────────────────────────────┤
│ WORLD 5: FINAL FORTRESS (3D WebGL Boss Battle Showdown) [Req: 11 ⭐]   │
│ Case 12: Mecha-Shellshock Boss   ──► FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 3. Step-by-Step Challenge Walkthrough (All 12 Cases)

### 🍄 WORLD 1: MUSHROOM VILLAGE (Sector 01)

#### Case 1: The Broken Notice Board (`/challenge/1`)
- **Category:** Web Forensics
- **Points / Rewards:** 100 PTS | +1 ⭐, +50 🪙
- **Boss Shield 1 Keyword:** `SECRET`
- **EXACT FLAG:** `FLAG{MUSHROOM_SECRET_OJAS_2026}`
- **Solution:**
  1. Click **[ TOGGLE DOM TREE INSPECTOR ]** in the challenge workbench.
  2. Inspect the HTML comment inside `#village-bulletin-board` (around line 94).
  3. Locate `<!-- cyber-heist-token: FLAG{MUSHROOM_SECRET_OJAS_2026} -->`.
  4. Submit the flag.

#### Case 2: The Suspicious Intercept (`/challenge/2`)
- **Category:** Cryptography
- **Points / Rewards:** 150 PTS | +1 ⭐, +75 🪙
- **Ciphertext:** `SYNT{YRGGRE_PVCURE_FBYIRQ_BWNF}`
- **EXACT FLAG:** `FLAG{LETTER_CIPHER_SOLVED_OJAS}`
- **Solution:**
  1. Identify the substitution as a **ROT-13** Caesar cipher (`SYNT` shifted 13 positions = `FLAG`).
  2. In the interactive workbench, drag the **CAESAR ROTATION SHIFT** slider to **`13`**.
  3. The decoded output turns green: `FLAG{LETTER_CIPHER_SOLVED_OJAS}`.
  4. Submit the flag.

---

### 🌲 WORLD 2: DARK FOREST (Sector 02 — Requires 2 ⭐)

#### Case 3: Deep Glitch in the Pines (`/challenge/3`)
- **Category:** Steganography
- **Points / Rewards:** 200 PTS | +1 ⭐, +100 🪙
- **Boss Shield 2 Keyword:** `PINES`
- **EXACT FLAG:** `FLAG{FOREST_PIXEL_STEGO_OJAS}`
- **Solution:**
  1. In the drone image visualizer, use the bitplane inspection buttons.
  2. Click **[ LSB BITPLANE 0 ]** or **[ GREEN PLANE ]**.
  3. The black background reveals fluorescent text: `FLAG{FOREST_PIXEL_STEGO_OJAS}`.
  4. Submit the flag.

#### Case 4: The Shadow Metadata Trail (`/challenge/4`)
- **Category:** OSINT & Forensics
- **Points / Rewards:** 200 PTS | +1 ⭐, +100 🪙
- **EXACT FLAG:** `FLAG{METADATA_TRAIL_REVEALED_OJAS}`
- **Solution:**
  1. Read through the RAW EXIF Metadata terminal on screen.
  2. Inspect the `UserComment` tag: `UserComment: FLAG{METADATA_TRAIL_REVEALED_OJAS}`.
  3. Copy and submit the flag.

#### Case 5: Corrupted Proxy Stream (`/challenge/5`)
- **Category:** Network Forensics
- **Points / Rewards:** 250 PTS | +1 ⭐, +125 🪙
- **Hex Dump:** `46 4c 41 47 7b 44 41 52 4b 5f 46 4f 52 45 53 54 5f 53 54 52 45 41 4d 5f 44 45 43 4f 44 45 44 7d`
- **EXACT FLAG:** `FLAG{DARK_FOREST_STREAM_DECODED}`
- **Solution:**
  1. Convert the hexadecimal byte pairs to ASCII text (`0x46` = 'F', `0x4C` = 'L', `0x41` = 'A', `0x47` = 'G', etc.).
  2. Decoded string reads: `FLAG{DARK_FOREST_STREAM_DECODED}`.
  3. Submit the flag.

---

### 👻 WORLD 3: HAUNTED MANSION (Sector 03 — Requires 5 ⭐)

#### Case 6: Phantom Directory Traversal (`/challenge/6`)
- **Category:** Web Security / Path Traversal
- **Points / Rewards:** 250 PTS | +1 ⭐, +125 🪙
- **EXACT FLAG:** `FLAG{BOO_GHOST_PATH_DISCOVERED}`
- **Solution:**
  1. Enter `/robots.txt` into the path explorer and click **FETCH**.
  2. Note the disallowed path: `Disallow: /secret_attic/ # Note: ghost_manifesto.bak contains sector vault key`.
  3. Update path to `/secret_attic/ghost_manifesto.bak` and click **FETCH**.
  4. The file contents reveal: `FLAG{BOO_GHOST_PATH_DISCOVERED}`.
  5. Submit the flag.

#### Case 7: Boo's Vault IDOR Manipulation (`/challenge/7`)
- **Category:** API Security (IDOR)
- **Points / Rewards:** 300 PTS | +1 ⭐, +150 🪙
- **Boss Shield 3 Keyword:** `BOO`
- **EXACT FLAG:** `FLAG{API_AUTH_BYPASS_OJAS}`
- **Solution:**
  1. Inspect the API request editor: guest ID is set to `1042`.
  2. Change `ENDPOINT PARAM (locker_id)` to `1`.
  3. Change `HEADER (X-Access-Level)` to `master_phantom`.
  4. Click **[ SEND INTERCEPTED API REQUEST ]**.
  5. King Boo's Vault locker #0001 responds with: `FLAG{API_AUTH_BYPASS_OJAS}`.
  6. Submit the flag.

#### Case 8: Poltergeist Session Forgery (`/challenge/8`)
- **Category:** Token Exploitation (JWT)
- **Points / Rewards:** 300 PTS | +1 ⭐, +150 🪙
- **EXACT FLAG:** `FLAG{SESSION_FORGERY_DETECTED_OJAS}`
- **Solution:**
  1. In the JWT Token Forge tool:
     - Change **TOKEN ROLE** from `guest` to `admin`.
     - Change **SIGNATURE ALGORITHM (alg)** from `HS256` to `none (Unsigned Bypass)`.
  2. Click **[ TRANSMIT FORGED SESSION COOKIE ]**.
  3. Server validates the unverified token and returns: `FLAG{SESSION_FORGERY_DETECTED_OJAS}`.
  4. Submit the flag.

---

### 🐢 WORLD 4: KOOPA HQ (Sector 04 — Requires 8 ⭐)

#### Case 9: The Framed Shellshock Recon (`/challenge/9`)
- **Category:** Incident Forensics
- **Points / Rewards:** 350 PTS | +1 ⭐, +175 🪙
- **EXACT FLAG:** `FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}`
- **Solution:**
  1. Inspect the terminal displaying `cat /home/shellshock/.bash_logout.bak`.
  2. Review the backdoor script injected 48 hours prior to the heist.
  3. Locate the embedded token: `FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}`.
  4. Submit the flag.

#### Case 10: Correlated SIEM Log Breaches (`/challenge/10`)
- **Category:** Threat Hunting / Log Analysis
- **Points / Rewards:** 350 PTS | +1 ⭐, +175 🪙
- **Boss Shield 4 Keyword:** `INSIDER`
- **EXACT FLAG:** `FLAG{CORRELATED_LOGS_INSIDER_OJAS}`
- **Solution:**
  1. Filter the SIEM logs query for `IP=10.99.13.37 AND STATUS=200`.
  2. Observe the successful call to `/internal/admin/override`.
  3. The `User-Agent` string contains:
     `Insider-Infiltrator/1.0 (FlagPayload: FLAG{CORRELATED_LOGS_INSIDER_OJAS})`.
  4. Submit the flag.

#### Case 11: Koopa Fortress Mainframe Bypass (`/challenge/11`)
- **Category:** SQL Injection
- **Points / Rewards:** 400 PTS | +1 ⭐, +200 🪙
- **EXACT FLAG:** `FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}`
- **Solution:**
  1. In the badge ID input, enter the standard SQL authentication bypass payload:
     `' OR '1'='1` (or `' OR 1=1`).
  2. Click **[ QUERY DB ]**.
  3. The database bypass triggers and dumps records; row 999 contains:
     `FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}`.
  4. Submit the flag.

---

### 🏰 WORLD 5: FINAL FORTRESS (Sector 05 — Requires 11 ⭐)

#### Case 12: Mecha-Shellshock Showdown (`/challenge/12`)
- **Category:** Master Synthesis & 3D Interactive Boss Fight
- **Points / Rewards:** 500 PTS | +2 ⭐, +300 🪙
- **EXACT MASTER FLAG:** `FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}`

##### 4 Quantum Shield Override Answers:
1. **Shield 1 (Sector 01: Mushroom Village):** Keyword in Case 1 HTML comment ➔ `SECRET`
2. **Shield 2 (Sector 02: Dark Forest):** Forest ridge location from Case 3 ➔ `PINES`
3. **Shield 3 (Sector 03: Haunted Mansion):** VIP locker owner in Case 7 ➔ `BOO`
4. **Shield 4 (Sector 04: Koopa HQ):** Threat actor User-Agent tag in Case 10 ➔ `INSIDER`

##### Final Victory Steps:
1. Enter each keyword into its corresponding quantum shield input and click **CRACK**.
2. As each shield cracks, it shatters in the 3D scene and turns green (`NEUTRALIZED ✅`).
3. Once all 4 shields are cracked, Mecha-Shellshock is defeated, and the Master Flag auto-populates:
   `FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}`.
4. Click **[ SUBMIT FLAG ]** to unlock the **[ 🏆 VIEW VICTORY CELEBRATION ]** portal (`/victory`) with the official championship diploma, 8-bit fanfare, and fireworks!

---

## 🛠️ 4. Quick Server & Admin Commands

- **Run Server:**
  ```powershell
  python app.py
  ```
- **Run Automated Verification Suite:**
  ```powershell
  python verify_ctf.py
  ```
- **Admin Portal URL:** `http://127.0.0.1:5000/admin`
- **Host Passkeys:**
  - Lead Host: `OJAS-HOST-ALPHA-7701`
  - Co-Host / Lab Moderator: `OJAS-HOST-BRAVO-9924`
  - Superadmin Fallback: `OJAS-HOST-SUPER-4418`
