# 🍄 MARIO: THE CYBER HEIST — HOST CREDENTIALS & MASTER ANSWER SCRIPT
**Event:** Chanakya University • OJAS Tech Fest 2026  
**Document Classification:** CONFIDENTIAL // EVENT HOST & ORGANIZER EYES ONLY  
**Do NOT Share This File With Participating Players!**

---

## 🔐 1. HOST ACCESS CREDENTIALS & SECURITY KEYS

To access the restricted Organizer Terminal, navigate in any browser to:  
👉 **`http://127.0.0.1:5000/admin`** (or click `🔐 ADMIN` in the top header/footer)

The server backend is hardcoded to accept any of the following **3 Secret Host Keys**:

| Priority | Role | Secret Host Passkey | Description & Usage |
| :--- | :--- | :--- | :--- |
| **Key 1** | **Primary Host Master Key** | `OJAS-HOST-ALPHA-7701` | Main credentials for the lead event organizer / host. |
| **Key 2** | **Secondary / Co-Host Key** | `OJAS-HOST-BRAVO-9924` | For assistant coordinators, lab moderators, and scorekeepers. |
| **Key 3** | **Superadmin Emergency Key** | `OJAS-HOST-SUPER-4418` | Emergency fallback override key. |

*(Legacy fallback key `OJAS_ADMIN_2026` is also active).*

### 🌐 Quick Game Links:
- **Game Start Screen:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/) *(LAN: `http://192.168.100.7:5000/`)*
- **Squad Registration:** [http://127.0.0.1:5000/briefing](http://127.0.0.1:5000/briefing)
- **3D World Map:** [http://127.0.0.1:5000/map](http://127.0.0.1:5000/map)
- **Live Leaderboard:** [http://127.0.0.1:5000/leaderboard](http://127.0.0.1:5000/leaderboard)
- **Admin Portal:** [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)
- **Full Links Directory:** See [`GAME_LINKS.md`](file:///c:/Users/ADMIN/OneDrive%20-%20Chanakya%20University/Desktop/Mario%20OJAS/GAME_LINKS.md) and [`GAME_LINKS.txt`](file:///c:/Users/ADMIN/OneDrive%20-%20Chanakya%20University/Desktop/Mario%20OJAS/GAME_LINKS.txt)

---

## 🎯 2. MASTER ANSWER SCRIPT & SOLUTIONS (ALL 12 CASES)

Below is the complete walkthrough, exact flag, and step-by-step forensic procedure for every challenge in the game.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  WORLD 1: MUSHROOM VILLAGE (Sector 01: Ground Zero)                                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  Case 1: The Broken Notice Board  ──► FLAG{MUSHROOM_SECRET_OJAS_2026}                 │
│  Case 2: The Suspicious Intercept ──► FLAG{LETTER_CIPHER_SOLVED_OJAS}                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  WORLD 2: DARK FOREST (Sector 02: Digital Woods - Unlocked at 2 Stars)                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  Case 3: Deep Glitch in the Pines ──► FLAG{FOREST_PIXEL_STEGO_OJAS}                   │
│  Case 4: The Shadow Metadata Trail──► FLAG{METADATA_TRAIL_REVEALED_OJAS}              │
│  Case 5: Corrupted Proxy Stream   ──► FLAG{DARK_FOREST_STREAM_DECODED}               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  WORLD 3: HAUNTED MANSION (Sector 03: Phantom Network - Unlocked at 5 Stars)          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  Case 6: Phantom Directory Hunt   ──► FLAG{BOO_GHOST_PATH_DISCOVERED}                 │
│  Case 7: Boo's Vault IDOR API     ──► FLAG{API_AUTH_BYPASS_OJAS}                      │
│  Case 8: Poltergeist JWT Forgery  ──► FLAG{SESSION_FORGERY_DETECTED_OJAS}             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  WORLD 4: KOOPA HQ (Sector 04: Industrial Bastion - Unlocked at 8 Stars)               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  Case 9: The Framed Shellshock    ──► FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}                │
│  Case 10: Correlated SIEM Logs    ──► FLAG{CORRELATED_LOGS_INSIDER_OJAS}              │
│  Case 11: Fortress SQLi Mainframe ──► FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  WORLD 5: FINAL FORTRESS (Sector 05: Master Vault - Unlocked at 11 Stars)              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  Case 12: Mecha-Shellshock Boss   ──► FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 🍄 WORLD 1: MUSHROOM VILLAGE (Sector 01)

#### Case 1: The Broken Notice Board (`/challenge/1`)
- **Category:** Web Forensics
- **Points:** 100 PTS | **Rewards:** +1 ⭐, +50 🪙
- **EXACT FLAG:** `FLAG{MUSHROOM_SECRET_OJAS_2026}`
- **Boss Shield 1 Keyword:** `SECRET`
- **Solution Walkthrough:**
  1. Click the **[ TOGGLE DOM TREE INSPECTOR ]** button in the interactive tool.
  2. Inspect the HTML source code comments inside `#village-bulletin-board`.
  3. Look at line 94: `<!-- cyber-heist-token: FLAG{MUSHROOM_SECRET_OJAS_2026} -->`.
  4. Paste into the Flag input and submit.

#### Case 2: The Suspicious Intercept (`/challenge/2`)
- **Category:** Cryptography
- **Points:** 150 PTS | **Rewards:** +1 ⭐, +75 🪙
- **Ciphertext:** `SYNT{YRGGRE_PVCURE_FBYIRQ_BWNF}`
- **EXACT FLAG:** `FLAG{LETTER_CIPHER_SOLVED_OJAS}`
- **Solution Walkthrough:**
  1. Notice that `SYNT` shifted by 13 positions in the alphabet becomes `FLAG` ($S \rightarrow F, Y \rightarrow L, N \rightarrow A, T \rightarrow G$).
  2. Drag the **CAESAR ROTATION SHIFT** slider in the workbench to **`13`**.
  3. The decoded string turns bright green: `FLAG{LETTER_CIPHER_SOLVED_OJAS}`.
  4. Paste and submit.

---

### 🌲 WORLD 2: DARK FOREST (Sector 02 - Unlocked at 2 Stars)

#### Case 3: Deep Glitch in the Pines (`/challenge/3`)
- **Category:** Steganography
- **Points:** 200 PTS | **Rewards:** +1 ⭐, +100 🪙
- **EXACT FLAG:** `FLAG{FOREST_PIXEL_STEGO_OJAS}`
- **Boss Shield 2 Keyword:** `PINES`
- **Solution Walkthrough:**
  1. The drone image visualizer has 4 bitplane buttons underneath.
  2. Click either **[ GREEN PLANE ]** or **[ LSB BITPLANE 0 ]**.
  3. The background renders black and reveals the concealed fluorescent ASCII text: `BITPLANE 0 CONCEALED PAYLOAD: FLAG{FOREST_PIXEL_STEGO_OJAS}`.
  4. Submit flag.

#### Case 4: The Shadow Metadata Trail (`/challenge/4`)
- **Category:** OSINT & Forensics
- **Points:** 200 PTS | **Rewards:** +1 ⭐, +100 🪙
- **EXACT FLAG:** `FLAG{METADATA_TRAIL_REVEALED_OJAS}`
- **Solution Walkthrough:**
  1. Inspect the RAW EXIF METADATA TERMINAL displayed on the left.
  2. Check the bottom tags:
     - `Software: CyberHeist_Stealth_Encoder`
     - `UserComment: FLAG{METADATA_TRAIL_REVEALED_OJAS}`
  3. Copy and submit the flag.

#### Case 5: Corrupted Proxy Stream (`/challenge/5`)
- **Category:** Network Forensics
- **Points:** 250 PTS | **Rewards:** +1 ⭐, +125 🪙
- **Hex Dump:** `46 4c 41 47 7b 44 41 52 4b 5f 46 4f 52 45 53 54 5f 53 54 52 45 41 4d 5f 44 45 43 4f 44 45 44 7d`
- **EXACT FLAG:** `FLAG{DARK_FOREST_STREAM_DECODED}`
- **Solution Walkthrough:**
  1. Convert each pair of hexadecimal numbers to standard ASCII ($0x46 = 'F', 0x4C = 'L', 0x41 = 'A', 0x47 = 'G'$).
  2. The reconstructed ASCII stream is `FLAG{DARK_FOREST_STREAM_DECODED}`.
  3. Submit flag.

---

### 👻 WORLD 3: HAUNTED MANSION (Sector 03 - Unlocked at 5 Stars)

#### Case 6: Phantom Directory Traversal (`/challenge/6`)
- **Category:** Web Security
- **Points:** 250 PTS | **Rewards:** +1 ⭐, +125 🪙
- **EXACT FLAG:** `FLAG{BOO_GHOST_PATH_DISCOVERED}`
- **Solution Walkthrough:**
  1. In the file explorer input, enter `/robots.txt` and click **FETCH**.
  2. Output returns: `Disallow: /secret_attic/ # Note: ghost_manifesto.bak contains sector vault key`.
  3. Change the path to `/secret_attic/ghost_manifesto.bak` (or `../../secret_attic/ghost_manifesto.bak`) and click **FETCH**.
  4. Response grants restricted access and displays: `FLAG{BOO_GHOST_PATH_DISCOVERED}`.

#### Case 7: Boo's Vault IDOR Manipulation (`/challenge/7`)
- **Category:** API Security
- **Points:** 300 PTS | **Rewards:** +1 ⭐, +150 🪙
- **EXACT FLAG:** `FLAG{API_AUTH_BYPASS_OJAS}`
- **Boss Shield 3 Keyword:** `BOO`
- **Solution Walkthrough:**
  1. Look at the API parameter fields: `ENDPOINT PARAM (locker_id)` and `HEADER (X-Access-Level)`.
  2. The guest ID is `1042`. Change `locker_id` to `1`.
  3. Set `HEADER (X-Access-Level)` to `master_phantom`.
  4. Click **[ SEND INTERCEPTED API REQUEST ]**.
  5. The API responds with King Boo's VIP Vault locker #0001 releasing: `FLAG{API_AUTH_BYPASS_OJAS}`.

#### Case 8: Poltergeist Session Forgery (`/challenge/8`)
- **Category:** Token Exploitation (JWT)
- **Points:** 300 PTS | **Rewards:** +1 ⭐, +150 🪙
- **EXACT FLAG:** `FLAG{SESSION_FORGERY_DETECTED_OJAS}`
- **Solution Walkthrough:**
  1. In the JWT Token Forge tool:
     - Change **TOKEN ROLE** from `guest` to `admin`.
     - Change **SIGNATURE ALGORITHM (alg)** from `HS256 (Signed)` to `none (Unsigned Bypass)`.
  2. Click **[ TRANSMIT FORGED SESSION COOKIE ]**.
  3. The server validates the `alg: none` payload without signature checking and outputs: `FLAG{SESSION_FORGERY_DETECTED_OJAS}`.

---

### 🐢 WORLD 4: KOOPA HQ (Sector 04 - Unlocked at 8 Stars)

#### Case 9: The Framed Shellshock Recon (`/challenge/9`)
- **Category:** Forensics
- **Points:** 350 PTS | **Rewards:** +1 ⭐, +175 🪙
- **EXACT FLAG:** `FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}`
- **Solution Walkthrough:**
  1. Inspect the terminal displaying `cat /home/shellshock/.bash_logout.bak`.
  2. The injected reverse shell payload shows that the server was compromised 48 hours prior to the heist.
  3. The token embedded inside the file is `FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}`.

#### Case 10: Correlated SIEM Log Breaches (`/challenge/10`)
- **Category:** Threat Hunting
- **Points:** 350 PTS | **Rewards:** +1 ⭐, +175 🪙
- **EXACT FLAG:** `FLAG{CORRELATED_LOGS_INSIDER_OJAS}`
- **Boss Shield 4 Keyword:** `INSIDER`
- **Solution Walkthrough:**
  1. Look at the filtered SIEM query for `IP=10.99.13.37 AND STATUS=200`.
  2. The successful request to `/internal/admin/override` contains the user agent:
     `User-Agent: Insider-Infiltrator/1.0 (FlagPayload: FLAG{CORRELATED_LOGS_INSIDER_OJAS})`.
  3. Notice also the parameter `token: "INSIDER"`.
  4. Submit flag.

#### Case 11: Koopa Fortress Mainframe Bypass (`/challenge/11`)
- **Category:** SQL Injection
- **Points:** 400 PTS | **Rewards:** +1 ⭐, +200 🪙
- **EXACT FLAG:** `FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}`
- **Solution Walkthrough:**
  1. In the badge ID input, enter the standard SQL authentication bypass tautology:
     `' OR '1'='1` (or `' OR 1=1`).
  2. Click **[ QUERY DB ]**.
  3. The SQL parser evaluates the condition as true, bypassing the query filter and dumping the database records.
  4. Root row 999 reveals: `FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}`.

---

### 🏰 WORLD 5: FINAL FORTRESS (Sector 05 - Unlocked at 11 Stars)

#### Case 12: Master Key Synthesis — Mecha-Shellshock Showdown (`/challenge/12`)
- **Category:** Master Synthesis & 3D Boss Battle
- **Points:** 500 PTS | **Rewards:** +2 ⭐, +300 🪙
- **EXACT MASTER FLAG:** `FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}`

##### 4 Quantum Shield Override Answers:
1. **Shield 1 (Sector 01: Mushroom Village)**:
   - *Question:* Secret keyword inside HTML comment on village board in Case 1?
   - **Answer:** `SECRET`
2. **Shield 2 (Sector 02: Dark Forest)**:
   - *Question:* Forested mountain ridge location surveyed in Case 3?
   - **Answer:** `PINES`
3. **Shield 3 (Sector 03: Haunted Mansion)**:
   - *Question:* Phantom entity owner of confidential VIP Vault locker #0001 in Case 7?
   - **Answer:** `BOO` (or `KING BOO`)
4. **Shield 4 (Sector 04: Koopa HQ)**:
   - *Question:* Rogue internal user-agent threat actor tag in SIEM logs in Case 10?
   - **Answer:** `INSIDER`

##### Completing the Showdown:
1. Type each answer into its respective shield input and click **CRACK** (or press `Enter`).
2. Each cracked shield shatters in the 3D WebGL scene and turns green `NEUTRALIZED ✅`.
3. When all 4 shields are neutralized, Mecha-Shellshock powers down, the Golden Star drops, and the synthesized Master Flag **automatically populates into the submission box**:
   `FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}`
4. Click **[ SUBMIT FLAG ]**.
5. The **[ 🏆 VIEW VICTORY CELEBRATION ]** button unlocks, leading to `/victory` with fireworks, 8-bit fanfare music, and the Official Champion Diploma!

---

## 🛠️ 3. HOST OPERATIONS QUICK REFERENCE

### 1. Registering Teams on Site
- Direct players to **[`http://127.0.0.1:5000/briefing`](http://127.0.0.1:5000/briefing)**.
- Have them type their squad name under **Register New Participating Squad** and click **DISPATCH NEW SQUAD**.
- They receive a unique Access Code (`OJAS-XXXXXX`) and 100 starter coins.

### 2. Helping Teams Recover Access Codes
- Go to `/admin` -> Tab 1 (**Squads Tracker & Results**).
- Find the squad in the table. Click the **`OJAS-XXXXXX 📋`** chip to copy their code.

### 3. Live Solve Matrix Monitoring
- Tab 1 displays a 12-cell matrix for each squad.
- Green cells (`✓`) indicate completed challenges.
- Gray cells (`·`) indicate unsolved challenges.
- Hover over any cell to see which challenge it is and when it was solved.

### 4. Live Submissions Audit
- Tab 2 displays every single flag attempt submitted in real time.
- Filter by `CORRECT ONLY (✅)` or `FAILED ONLY (❌)` to monitor team attempts.

### 5. Exporting Final Results
- Tab 3 (**Podium & Export Reports**) provides:
  - **Download CSV**: Downloads `ojas_ctf_results.csv` with final ranks, scores, stars, and solve counts.
  - **Download JSON**: Full API dump for software integrations.
  - **Print Official Report**: Formatted sheet for prize distribution and announcements.

### 6. Emergency Developer / Testing Commands
- **Grant All Stars (Instant Unlock):** Click `⭐ DEVELOPER UNLOCK` in Tab 4 to grant 12 stars and 1000 coins to your active test account.
- **Factory Database Reset:** Click `⚠️ FACTORY RESET CTF DATABASE` in Tab 4 to wipe all scores and reset the CTF to factory state for the start of the tournament.
