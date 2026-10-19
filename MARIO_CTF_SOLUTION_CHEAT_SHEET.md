# 🍄 MARIO: THE CYBER HEIST — MASTER SOLUTION & EXPLOITATION CHEAT SHEET
**Event:** Chanakya University • OJAS Tech Fest 2026  
**Document Classification:** CONFIDENTIAL // HOST, JURY & ORGANIZER EYES ONLY  
**Purpose:** Technical Assessment, Evaluation, and Official Answer Key  

---

## 🔐 1. HOST ACCESS & CREDENTIALS QUICK REFERENCE

- **Host Admin Portal:** `http://127.0.0.1:5000/admin` (or `https://mario-ctf.onrender.com/admin`)
- **Restricted Live Leaderboard:** `http://127.0.0.1:5000/leaderboard` (Restricted to Host Key)
- **Host Secret Security Keys:**
  - **Primary Host Key:** `OJAS-HOST-ALPHA-7701`
  - **Secondary Co-Host Key:** `OJAS-HOST-BRAVO-9924`
  - **Superadmin Emergency Key:** `OJAS-HOST-SUPER-4418`
  - *(Legacy fallback:* `OJAS_ADMIN_2026`*)*

---

## 🎯 2. MASTER QUICK-REFERENCE ANSWER TABLE

| Case # | Challenge Title | Sector | Category | Pts | Exact Flag | Shield Key |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: |
| **#1** | The Broken Notice Board | S1: Mushroom Village | Web / DOM Forensics | 100 | `FLAG{MUSHROOM_SECRET_OJAS_2026}` | **`SECRET`** |
| **#2** | The Suspicious Intercept | S1: Mushroom Village | Cryptography (ROT-13) | 150 | `FLAG{LETTER_CIPHER_SOLVED_OJAS}` | — |
| **#3** | Deep Glitch in the Pines | S2: Dark Forest | Steganography (LSB) | 200 | `FLAG{FOREST_PIXEL_STEGO_OJAS}` | **`PINES`** |
| **#4** | The Shadow Metadata Trail | S2: Dark Forest | OSINT / EXIF Forensics | 200 | `FLAG{METADATA_TRAIL_REVEALED_OJAS}` | — |
| **#5** | Corrupted Proxy Stream | S2: Dark Forest | Network Hexdump | 250 | `FLAG{DARK_FOREST_STREAM_DECODED}` | — |
| **#6** | Phantom Directory Traversal | S3: Haunted Mansion | Web Security / Traversal | 250 | `FLAG{BOO_GHOST_PATH_DISCOVERED}` | — |
| **#7** | Boo's Vault IDOR Manipulation| S3: Haunted Mansion | API Security / IDOR | 300 | `FLAG{API_AUTH_BYPASS_OJAS}` | **`BOO`** |
| **#8** | Poltergeist Session Forgery | S3: Haunted Mansion | JWT Algorithm Confusion | 300 | `FLAG{SESSION_FORGERY_DETECTED_OJAS}`| — |
| **#9** | The Framed Shellshock Recon | S4: Koopa HQ | Host Persistence Forensics | 350 | `FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}` | — |
| **#10**| Correlated SIEM Log Breaches | S4: Koopa HQ | Threat Hunting / SIEM | 350 | `FLAG{CORRELATED_LOGS_INSIDER_OJAS}` | **`INSIDER`** |
| **#11**| Fortress Mainframe Bypass | S4: Koopa HQ | SQL Injection (SQLi) | 400 | `FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}` | — |
| **#12**| Mecha-Shellshock Showdown | S5: Final Fortress | Master Boss Synthesis | 500 | `FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}` | **4 KEYS** |

---

## 🔬 3. DETAILED CASE-BY-CASE BREAKDOWN: "WHY" & "HOW TO CRACK"

---

### CASE 1: The Broken Notice Board
* **Sector:** Sector 01: Mushroom Village (Ground Zero) • Web Forensics
* **Reward:** 100 PTS | +1 ⭐ | +50 🪙
* **EXACT FLAG:** `FLAG{MUSHROOM_SECRET_OJAS_2026}`
* **Boss Shield 1 Keyword:** `SECRET`

#### 🧠 WHY (Vulnerability Concept):
**Insecure Information Disclosure via Client-Side Source Comments (CWE-615)**  
Developers frequently leave staging credentials, test tokens, or private notes in HTML comments (`<!-- ... -->`). Because web browsers download the raw HTML markup before rendering, comments are ignored by the visual parser but remain fully readable in plaintext by anyone inspecting the DOM.

#### ⚡ HOW TO CRACK:
1. In the Case 1 workbench, click **`[ TOGGLE DOM TREE INSPECTOR ]`** (or open browser DevTools with `F12` / `Ctrl+Shift+I`).
2. Expand `#village-bulletin-board` and inspect the comment block around line 94.
3. Locate: `<!-- cyber-heist-token: FLAG{MUSHROOM_SECRET_OJAS_2026} -->`.
4. Submit the flag and note the keyword **`SECRET`** for World 5.

---

### CASE 2: The Suspicious Intercept
* **Sector:** Sector 01: Mushroom Village • Cryptography
* **Reward:** 150 PTS | +1 ⭐ | +75 🪙
* **Ciphertext:** `SYNT{YRGGRE_PVCURE_FBYIRQ_BWNF}`
* **EXACT FLAG:** `FLAG{LETTER_CIPHER_SOLVED_OJAS}`

#### 🧠 WHY (Vulnerability Concept):
**Weak Obfuscation / Insecure Classical Substitution (CWE-327)**  
The intercepted message was obscured with ROT-13 (Caesar shift of 13 characters). Fixed-shift substitution ciphers offer zero cryptographic entropy. Attackers easily deduce the key using known-plaintext analysis ($S \rightarrow F, Y \rightarrow L, N \rightarrow A, T \rightarrow G$).

#### ⚡ HOW TO CRACK:
1. Observe that `SYNT` shifted backwards by 13 letters produces `FLAG`.
2. In the workbench, drag the **CAESAR ROTATION SHIFT** slider to **`13`**.
3. The decrypted text turns green: `FLAG{LETTER_CIPHER_SOLVED_OJAS}`.
4. Copy and submit the flag.

---

### CASE 3: Deep Glitch in the Pines
* **Sector:** Sector 02: Dark Forest (Digital Woods • Requires 2 ⭐) • Steganography
* **Reward:** 200 PTS | +1 ⭐ | +100 🪙
* **EXACT FLAG:** `FLAG{FOREST_PIXEL_STEGO_OJAS}`
* **Boss Shield 2 Keyword:** `PINES`

#### 🧠 WHY (Vulnerability Concept):
**Least Significant Bit (LSB) Image Steganography**  
Digital 24-bit RGB images store colors using 8 bits (0–255) per color channel. Altering only the lowest bit (Bit 0) alters pixel brightness by only $1/256$—completely invisible to the naked human eye. Threat actors exploit this perceptual threshold to hide ASCII/binary payloads inside innocent-looking images.

#### ⚡ HOW TO CRACK:
1. Open the drone surveillance viewer in Case 3.
2. Under the canvas, click **`[ GREEN PLANE ]`** or **`[ LSB BITPLANE 0 ]`**.
3. The image contrast strips away high-order pixels, exposing the hidden fluorescent ASCII text: `BITPLANE 0 CONCEALED: FLAG{FOREST_PIXEL_STEGO_OJAS}`.
4. Submit the flag and note keyword **`PINES`** for World 5.

---

### CASE 4: The Shadow Metadata Trail
* **Sector:** Sector 02: Dark Forest • OSINT & Forensics
* **Reward:** 200 PTS | +1 ⭐ | +100 🪙
* **EXACT FLAG:** `FLAG{METADATA_TRAIL_REVEALED_OJAS}`

#### 🧠 WHY (Vulnerability Concept):
**File Header & EXIF Metadata Leakage (CWE-200)**  
Modern media files embed non-visual metadata headers (EXIF, IPTC, XMP) containing camera specs, GPS coordinates, timestamps, and encoder notes. Failing to sanitize or strip EXIF metadata before hosting files publicly leaks forensic artifacts.

#### ⚡ HOW TO CRACK:
1. Inspect the **RAW EXIF METADATA TERMINAL** in Case 4.
2. Scroll through standard headers (Aperture, Focal Length, Sensor).
3. Find the custom vendor tags:
   - `Software: CyberHeist_Stealth_Encoder`
   - `UserComment: FLAG{METADATA_TRAIL_REVEALED_OJAS}`
4. Copy and submit the flag.

---

### CASE 5: Corrupted Proxy Stream
* **Sector:** Sector 02: Dark Forest • Network Forensics
* **Reward:** 250 PTS | +1 ⭐ | +125 🪙
* **Hex Dump:** `46 4c 41 47 7b 44 41 52 4b 5f 46 4f 52 45 53 54 5f 53 54 52 45 41 4d 5f 44 45 43 4f 44 45 44 7d`
* **EXACT FLAG:** `FLAG{DARK_FOREST_STREAM_DECODED}`

#### 🧠 WHY (Vulnerability Concept):
**Cleartext Network Transmission (CWE-319)**  
The rogue network proxy transmitted data across an unencrypted TCP socket. Even when represented as raw hex pairs, cleartext traffic retains 1-to-1 ASCII byte correspondence, making it trivial for packet analysts to reconstruct payloads.

#### ⚡ HOW TO CRACK:
1. Convert each hex pair into ASCII characters:
   - `0x46 = 'F'`, `0x4C = 'L'`, `0x41 = 'A'`, `0x47 = 'G'`, `0x7B = '{'`, `0x44 = 'D'`, etc.
2. Use the built-in workbench decoder or python (`bytes.fromhex('464c...').decode()`).
3. Output reveals: `FLAG{DARK_FOREST_STREAM_DECODED}`.

---

### CASE 6: Phantom Directory Traversal
* **Sector:** Sector 03: Haunted Mansion (Phantom Network • Requires 5 ⭐) • Web Security
* **Reward:** 250 PTS | +1 ⭐ | +125 🪙
* **EXACT FLAG:** `FLAG{BOO_GHOST_PATH_DISCOVERED}`

#### 🧠 WHY (Vulnerability Concept):
**Predictable Resource Location via `robots.txt` & Path Traversal (CWE-538)**  
Administrators often place sensitive directory names into `robots.txt` hoping search engines ignore them ("security through obscurity"). Attackers specifically audit `robots.txt` to find sensitive backup files (`.bak`), which frequently lack proper authorization controls.

#### ⚡ HOW TO CRACK:
1. In the Mansion File Explorer, type `/robots.txt` and click **FETCH**.
2. Output discloses: `Disallow: /secret_attic/ # Note: ghost_manifesto.bak contains sector vault key`.
3. Change the input path to `/secret_attic/ghost_manifesto.bak` and click **FETCH**.
4. The server returns the leaked backup document: `FLAG{BOO_GHOST_PATH_DISCOVERED}`.

---

### CASE 7: Boo's Vault IDOR Manipulation
* **Sector:** Sector 03: Haunted Mansion • API Security
* **Reward:** 300 PTS | +1 ⭐ | +150 🪙
* **EXACT FLAG:** `FLAG{API_AUTH_BYPASS_OJAS}`
* **Boss Shield 3 Keyword:** `BOO`

#### 🧠 WHY (Vulnerability Concept):
**Insecure Direct Object Reference / Broken Object Level Authorization (OWASP API1 / BOLA)**  
The backend API blindly trusts client-provided parameters (`locker_id`) and header values (`X-Access-Level`) without verifying whether the authenticated user has legitimate authorization to access King Boo's private vault #0001.

#### ⚡ HOW TO CRACK:
1. Look at the API parameters: Guest locker is `1042` with header `X-Access-Level: guest_phantom`.
2. Change parameter `locker_id` to VIP locker `1`.
3. Change header `X-Access-Level` to `master_phantom`.
4. Click **`[ SEND INTERCEPTED API REQUEST ]`**.
5. King Boo's VIP locker opens, returning: `FLAG{API_AUTH_BYPASS_OJAS}`.
6. Note keyword **`BOO`** for World 5.

---

### CASE 8: Poltergeist Session Forgery
* **Sector:** Sector 03: Haunted Mansion • JWT Token Security
* **Reward:** 300 PTS | +1 ⭐ | +150 🪙
* **EXACT FLAG:** `FLAG{SESSION_FORGERY_DETECTED_OJAS}`

#### 🧠 WHY (Vulnerability Concept):
**JWT 'alg: none' Signature Verification Bypass (CWE-347)**  
Vulnerable JWT libraries allow the client to specify the cryptographic signing algorithm in the header. If the client sends `"alg": "none"`, the library skips cryptographic signature validation entirely, allowing attackers to elevate their role from `guest` to `admin` by modifying the JSON payload.

#### ⚡ HOW TO CRACK:
1. In the JWT Token Forge tool:
   - Change **TOKEN ROLE** from `guest` to `admin`.
   - Change **SIGNATURE ALGORITHM (alg)** from `HS256 (Signed)` to `none (Unsigned Bypass)`.
2. Notice the signature part of the token is removed: `eyJhbGciOiJub25lIn0... .`.
3. Click **`[ TRANSMIT FORGED SESSION COOKIE ]`**.
4. The server accepts the forged admin cookie and returns: `FLAG{SESSION_FORGERY_DETECTED_OJAS}`.

---

### CASE 9: The Framed Shellshock Recon
* **Sector:** Sector 04: Koopa HQ (Industrial Bastion • Requires 8 ⭐) • Host Forensics
* **Reward:** 350 PTS | +1 ⭐ | +175 🪙
* **EXACT FLAG:** `FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}`

#### 🧠 WHY (Vulnerability Concept):
**Linux Host Persistence & Account Tampering Forensics**  
Intruders maintaining persistent access to compromised Linux hosts often tamper with shell termination files (`~/.bash_logout`) or profile scripts. Inspecting hidden dot-files and backup copies exposes implanted reverse-shell backdoors and forensic proof that an account was framed.

#### ⚡ HOW TO CRACK:
1. In the terminal workbench, inspect the backup file: `cat /home/shellshock/.bash_logout.bak`.
2. Review the reverse shell payload injected 48 hours prior to the heist.
3. Extract the forensic token embedded in the script: `FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}`.

---

### CASE 10: Correlated SIEM Log Breaches
* **Sector:** Sector 04: Koopa HQ • Threat Hunting & SIEM Analysis
* **Reward:** 350 PTS | +1 ⭐ | +175 🪙
* **EXACT FLAG:** `FLAG{CORRELATED_LOGS_INSIDER_OJAS}`
* **Boss Shield 4 Keyword:** `INSIDER`

#### 🧠 WHY (Vulnerability Concept):
**Threat Hunting: Isolating Anomalous User-Agents in Access Logs (MITRE ATT&CK T1071)**  
In high-volume access logs, automated attack scripts leave distinctive signatures. By filtering for pivot IP addresses and successful HTTP 200 responses on administrative endpoints, analysts detect custom User-Agent strings and embedded exploit parameters.

#### ⚡ HOW TO CRACK:
1. In the SIEM log viewer, apply the filter: `IP=10.99.13.37 AND STATUS=200`.
2. Find the successful request to `/internal/admin/override`.
3. Inspect the User-Agent header:
   `User-Agent: Insider-Infiltrator/1.0 (FlagPayload: FLAG{CORRELATED_LOGS_INSIDER_OJAS})`.
4. Note the threat tag **`INSIDER`** for World 5.

---

### CASE 11: Fortress Mainframe Bypass
* **Sector:** Sector 04: Koopa HQ • SQL Injection
* **Reward:** 400 PTS | +1 ⭐ | +200 🪙
* **EXACT FLAG:** `FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}`

#### 🧠 WHY (Vulnerability Concept):
**SQL Injection via Dynamic String Concatenation (CWE-89)**  
The backend executes raw query construction: `SELECT * FROM employees WHERE badge_id = '{input}'`. Because user input is concatenated without parameterized queries or prepared statements, injecting a boolean tautology (`' OR '1'='1`) forces the `WHERE` clause to evaluate to true for every single record in the table.

#### ⚡ HOW TO CRACK:
1. In the Koopa Security Badge terminal, enter the tautology payload: `' OR '1'='1` (or `' OR 1=1 --`).
2. Click **`[ QUERY DB ]`**.
3. The SQL engine bypasses authentication and dumps the entire employee table.
4. Record #999 reveals root archive token: `FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}`.

---

### CASE 12: Mecha-Shellshock Showdown (Master Core)
* **Sector:** Sector 05: Final Fortress (Master Vault • Requires 11 ⭐) • Boss Synthesis
* **Reward:** 500 PTS | +2 ⭐ | +300 🪙
* **EXACT MASTER FLAG:** `FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}`

#### 🧠 WHY (Vulnerability Concept):
**Multi-Vector Intelligence Synthesis & Defense-in-Depth Breach**  
The Final Boss represents an integrated cryptographic perimeter. Its 4 quantum shields cannot be brute-forced; they require synthesizing the 4 intelligence keywords gathered across the previous 4 sectors: DOM comment keyword, stego ridge name, VIP vault owner, and internal threat tag.

#### ⚡ HOW TO CRACK:
1. Input the 4 Sector Shield keywords into their respective terminals:
   * **Shield 1 (Sector 01: Mushroom Village):** `SECRET`
   * **Shield 2 (Sector 02: Dark Forest):** `PINES`
   * **Shield 3 (Sector 03: Haunted Mansion):** `BOO`
   * **Shield 4 (Sector 04: Koopa HQ):** `INSIDER`
2. Click **CRACK ⚡** on each shield. Each shield shatters and turns green (`NEUTRALIZED ✅`).
3. The moment the 4th shield is cracked:
   * Mecha-Shellshock powers down and drops the Golden Star in 3D.
   * The Master Vault unlocks, and **the Master Flag appears automatically in a glowing reveal banner and pre-populates into the flag input**:
     `FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}`
4. Click **`[ 🌟 SUBMIT MASTER FLAG ]`**.
5. The competition timer freezes permanently, locking the student's final score and ranking, and unlocks the Champion Ceremony!

---

## 🛠️ 4. HOST LIVE OPERATIONS & EVENT DAY CHEAT SHEET

| Issue / Scenario | Host Action & Quick Resolution |
| :--- | :--- |
| **Student forgot their Access Code** | Go to `/admin` -> Tab 1. Find the student and click the `OJAS-XXXXXX 📋` chip. Alternatively, students can reconnect by typing their **Register Number / USN** directly on the Briefing screen. |
| **Student stuck on Boss Battle** | Verify they entered the 4 sector keywords: `SECRET`, `PINES`, `BOO`, `INSIDER`. Neutralizing all 4 triggers automatic flag reveal. |
| **Accidental "Stop Mission" click** | Have the student navigate to `/end` (Debrief screen). Click **`🔄 REOPEN / RESUME MISSION`** to unfreeze their timer and resume the run. |
| **Viewing Live Leaderboard** | The public cannot view the leaderboard. Only the host can access `/leaderboard` by entering any Host Key (`OJAS-HOST-ALPHA-7701`). |
| **Factory Reset for Event Start** | In `/admin` -> Tab 4, click **`⚠️ FACTORY RESET CTF DATABASE`** (or call `admin_reset_system()`). This purges all test data and sets status to `LOBBY` with 0 teams. |
