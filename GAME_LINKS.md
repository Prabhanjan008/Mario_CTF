# 🍄 MARIO: THE CYBER HEIST — MASTER LINKS DIRECTORY
**Event:** Chanakya University • OJAS Tech Fest 2026  
**Game:** 3D Mario Cybersecurity CTF Heist Adventure  
**Server Status:** Active & Running (Port 5000)

---

## 🎮 LIVE TOURNAMENT FLOW (HOW IT WORKS ON GAME DAY)

1. **Host Publishes the Link:** Share `http://192.168.100.7:5000/` (or localhost for testing) with all participating students.
2. **Students Register Squads:** Students click *"Register Squad"* at `/briefing`, enter their Squad Name and Lead Handle, and receive their unique Crockford Base32 Access Code (e.g. `OJAS-K7M9P2X4`).
3. **Teammates Join:** Teammates enter that Access Code on their laptops/phones to join the same squad.
4. **Pre-Game Standby Lobby (`/lobby`):** All students gather in the live Mario Mission Radar Waiting Room. Screen displays registered squad members, live count of connected squads, and polls for Host Launch.
5. **Host Launches the Game (`/admin`):** The Host logs in at `/admin` using Host Passkey (`OJAS-HOST-ALPHA-7701`), sees all connected squads, and clicks **`[ 🚀 START GAME FOR ALL SQUADS ]`**.
6. **Instant Auto-Warp:** The instant the host starts the game, all students' screens play a retro Mario level-start chime and automatically warp directly into the **3D Cyber World Map (`/map`)** to begin solving!

---

## 🌐 1. MAIN GAME NAVIGATION LINKS

### On the Host Laptop (Localhost):
* 📋 **Squad Registration & Join:** [http://127.0.0.1:5000/briefing](http://127.0.0.1:5000/briefing)  
  *(Students enter squad name or access code to join)*
* 🛰️ **Pre-Game Standby Lobby:** [http://127.0.0.1:5000/lobby](http://127.0.0.1:5000/lobby)  
  *(Live waiting room radar with auto-warp when host starts game)*
* 🗺️ **3D Interactive World Map:** [http://127.0.0.1:5000/map](http://127.0.0.1:5000/map)  
  *(Unlocks automatically when host dispatches the mission)*
* 🏆 **Live Competition Leaderboard:** [http://127.0.0.1:5000/leaderboard](http://127.0.0.1:5000/leaderboard)  
  *(Real-time scores, star rankings, solve times)*
* 🏁 **Mission Debrief & Official End Screen:** [http://127.0.0.1:5000/end](http://127.0.0.1:5000/end)  
* 👑 **Victory Ceremony (Post-Boss):** [http://127.0.0.1:5000/victory](http://127.0.0.1:5000/victory)  

---

### For Other Laptops / Devices (Connected to Same Wi-Fi / LAN):
Share this link on the projector or lab boards:

* 📋 **Student Registration & Lobby:** `http://192.168.100.7:5000/`
* 🛰️ **Waiting Room:** `http://192.168.100.7:5000/lobby`
* 🏆 **Public Live Leaderboard:** `http://192.168.100.7:5000/leaderboard`

---

## 👑 2. RESTRICTED HOST & ORGANIZER CONTROL DECK (CONFIDENTIAL)

* 🔐 **Host Admin Portal:** [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)  
  *(LAN Link: `http://192.168.100.7:5000/admin`)*

### Host Actions in the Admin Dashboard:
* **`[ 🚀 START GAME FOR ALL SQUADS ]`**: Dispatches the competition, starts all squad timers, and auto-warps all students into the game.
* **`[ ⏸️ PAUSE / RESUME ]`**: Temporarily halts submissions and timers.
* **`[ 🏁 CONCLUDE ]`**: Stops submissions and freezes final official podium.
* **`[ 🧹 PURGE TEST SQUADS (CLEAN LOBBY) ]`**: Resets the entire database to a clean, 0-squad lobby ready for students.
* **`[ 📢 BROADCAST ]`**: Sends real-time announcements directly to all students' HUDs.

### Secret Host Authentication Keys:
| Priority | Key Role | Secret Passkey |
| :--- | :--- | :--- |
| **Key 1** | **Primary Master Host Key** | `OJAS-HOST-ALPHA-7701` |
| **Key 2** | **Secondary / Co-Host Key** | `OJAS-HOST-BRAVO-9924` |
| **Key 3** | **Superadmin Emergency Key** | `OJAS-HOST-SUPER-4418` |

### Host Export Endpoints:
* 📥 **Download Standings CSV:** [http://127.0.0.1:5000/api/admin/export/csv](http://127.0.0.1:5000/api/admin/export/csv)
* 📥 **View Standings JSON:** [http://127.0.0.1:5000/api/admin/export/json](http://127.0.0.1:5000/api/admin/export/json)
* ⚡ **Health Check Endpoint:** [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health)

---

## 🎯 3. DIRECT CHALLENGE CASE LINKS (12 INVESTIGATIONS)

### Sector 01: Mushroom Village (Ground Zero)
* **Case 1 (Web Forensics):** [http://127.0.0.1:5000/challenge/1](http://127.0.0.1:5000/challenge/1)  
  *Flag: `FLAG{MUSHROOM_SECRET_OJAS_2026}`*
* **Case 2 (Cryptography / ROT13):** [http://127.0.0.1:5000/challenge/2](http://127.0.0.1:5000/challenge/2)  
  *Flag: `FLAG{LETTER_CIPHER_SOLVED_OJAS}`*

### Sector 02: Dark Forest (Digital Woods — Unlocks at 2 Stars)
* **Case 3 (Steganography LSB):** [http://127.0.0.1:5000/challenge/3](http://127.0.0.1:5000/challenge/3)  
  *Flag: `FLAG{FOREST_PIXEL_STEGO_OJAS}`*
* **Case 4 (OSINT & EXIF Metadata):** [http://127.0.0.1:5000/challenge/4](http://127.0.0.1:5000/challenge/4)  
  *Flag: `FLAG{METADATA_TRAIL_REVEALED_OJAS}`*
* **Case 5 (Network Hex Stream):** [http://127.0.0.1:5000/challenge/5](http://127.0.0.1:5000/challenge/5)  
  *Flag: `FLAG{DARK_FOREST_STREAM_DECODED}`*

### Sector 03: Haunted Mansion (Phantom Network — Unlocks at 5 Stars)
* **Case 6 (Web Directory Traversal):** [http://127.0.0.1:5000/challenge/6](http://127.0.0.1:5000/challenge/6)  
  *Flag: `FLAG{BOO_GHOST_PATH_DISCOVERED}`*
* **Case 7 (API IDOR Vault):** [http://127.0.0.1:5000/challenge/7](http://127.0.0.1:5000/challenge/7)  
  *Flag: `FLAG{API_AUTH_BYPASS_OJAS}`*
* **Case 8 (JWT Session Forgery):** [http://127.0.0.1:5000/challenge/8](http://127.0.0.1:5000/challenge/8)  
  *Flag: `FLAG{SESSION_FORGERY_DETECTED_OJAS}`*

### Sector 04: Koopa HQ (Industrial Bastion — Unlocks at 8 Stars)
* **Case 9 (Forensic Recon & Reverse Shell):** [http://127.0.0.1:5000/challenge/9](http://127.0.0.1:5000/challenge/9)  
  *Flag: `FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}`*
* **Case 10 (SIEM Log Threat Hunt):** [http://127.0.0.1:5000/challenge/10](http://127.0.0.1:5000/challenge/10)  
  *Flag: `FLAG{CORRELATED_LOGS_INSIDER_OJAS}`*
* **Case 11 (SQL Injection Console):** [http://127.0.0.1:5000/challenge/11](http://127.0.0.1:5000/challenge/11)  
  *Flag: `FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}`*

### Sector 05: Final Fortress (Master Vault — Unlocks at 11 Stars)
* **Case 12 (3D Boss Arena — Mecha-Shellshock):** [http://127.0.0.1:5000/challenge/12](http://127.0.0.1:5000/challenge/12)  
  *(Shortcut: [http://127.0.0.1:5000/boss](http://127.0.0.1:5000/boss))*  
  *Shield Codes: `SECRET` • `PINES` • `BOO` • `INSIDER`*  
  *Master Flag: `FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}`*

---

## 📄 4. LOCAL DOCUMENTATION FILES

* 📖 **Master Answer Script & Guide:** [HOST_CREDENTIALS_AND_ANSWER_KEY.md](file:///c:/Users/ADMIN/OneDrive%20-%20Chanakya%20University/Desktop/Mario%20OJAS/HOST_CREDENTIALS_AND_ANSWER_KEY.md)
* 📋 **Project Walkthrough & Feature Summary:** [walkthrough.md](file:///C:/Users/ADMIN/.gemini/antigravity-ide/brain/8b8c81e1-d40f-4683-a21d-8fedaba2d31f/walkthrough.md)
