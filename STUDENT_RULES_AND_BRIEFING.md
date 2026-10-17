# 🍄 MARIO: THE CYBER HEIST
### OJAS Tech Fest 2026 — Official Cybersecurity CTF Briefing & Rules

Welcome, Investigators! You have been recruited by the Mushroom Kingdom Cyber Incident Response Team (MK-CIRT) to investigate the kingdom’s greatest security breach.

---

## 📖 Mission Background & Objective

At **03:14:07 AM**, the Master Sanctum vault security perimeter collapsed. The kingdom’s core power source, **THE GOLDEN STAR**, was forcibly exfiltrated by a rogue cyber syndicate operating under the alias **`PHANTOM_SHROOM`**.

Your objective is to navigate the **Interactive 3D World Map**, analyze forensic evidence across 4 compromised sectors, crack cryptographic ciphers, breach firewalls, and infiltrate Bowser’s Final Fortress to recover the Golden Star.

---

## 🗺️ Sector Progression & World Map

The competition spans **5 progressive sectors** containing **12 forensic cases**:

| Sector | World Name | Category Focus | Required Stars |
| :---: | :--- | :--- | :---: |
| **01** | **Mushroom Village** | Digital Forensics, PCAP Packet Analysis, Linux Permissions | **0 ⭐ (Unlocked)** |
| **02** | **Dark Forest** | Web Exploitation, Hash Cracking & Rainbow Tables, XSS Sanitization | **2 ⭐** |
| **03** | **Haunted Mansion** | Python Bytecode Reverse Engineering, Buffer Overflow, Firmware Forensics | **5 ⭐** |
| **04** | **Koopa HQ** | JWT Secret Forgery, Insecure AWS S3 Cloud Bucket Enumeration | **8 ⭐** |
| **05** | **Final Fortress** | **Boss Showdown** (Shatter 4 Sector Shields → Extract Master Flag) | **11 ⭐** |

---

## 🎮 Game Mechanics & Scoring Economy

### 1. 🏆 Forensic Points (Score)
* Each solved case awards points (ranging from **100 to 500 PTS** based on difficulty).
* Points determine your ranking on the **Live Leaderboard**.

### 2. ⭐ Golden Stars
* Every standard forensic case (Cases 1–11) cleared awards **1 Golden Star**.
* Golden Stars unlock higher-tier sectors on the 3D World Map.
* **11 Stars** are required to unlock the quantum firewall guarding Sector 05: Final Fortress.

### 3. 🪙 Cyber Coins & Hints
* Every investigator starts with **100 Cyber Coins**.
* Solving challenges earns bonus coins.
* **Interactive 3D ? Blocks:** Floating Question Mark blocks on the 3D World Map award extra coins when clicked!
* **Hints:** If you get stuck, you can spend Cyber Coins inside the challenge workbench to decrypt progressive forensic hints.

### 4. ⏱️ Competition Timer
* An authoritative, tamper-proof competition timer tracks your mission runtime.
* The timer starts when the tournament director gives the dispatch signal or upon your first case engagement.
* The clock automatically freezes the exact millisecond you successfully submit the Final Boss flag or click **Conclude Mission**.

---

## 👤 Solo Operative System (Individual Competition)

* **Individual Play:** This is a strictly **Solo / 1-vs-All** tournament. Every investigator competes independently on their own laptop or workstation.
* **Personal Access Code:** When you register your detective alias, you receive a unique cryptographic **Access Code** (e.g. `OJAS-W7KP-92RM`).
* **Session Portability:** If your browser closes, battery runs out, or you change workstations, simply enter your personal Access Code on the portal to resume your exact progress!
* **Independent Score Ledger:** Your solved flags, recovered stars, cyber coins, and monotonic mission timer are tracked uniquely to your operative account.

---

## 📜 Official Tournament Rules

### 1. 🚩 Flag Submission Format
* All flags follow the standard format:
  ```text
  FLAG{SAMPLE_FLAG_TEXT}
  ```
* Flags are **case-sensitive** and must include the `FLAG{...}` wrapper unless explicitly noted in the challenge brief.

### 2. 🛡️ Anti-Brute-Force & Rate Limiting
* Automated dictionary attacks or script-based brute forcing against the submission box will trigger an automatic rate-limit penalty (**maximum 10 submissions per 30 seconds** per participant).

### 3. 🛑 Prohibited Actions (Zero Tolerance — Immediate Disqualification)
* **No attacking the platform:** Do NOT launch DoS/DDoS attacks, SQL injections, or port scans against the host server (`http://...`). All challenges provide self-contained sandboxes or downloadable evidence artifacts.
* **No collusion or answer sharing:** Do NOT share flags, answers, access codes, or hints with any other participant. This is an individual 1-vs-All tournament.
* **No tampering with other participants:** Do NOT attempt to hijack or use another investigator's session or access code.

### 4. ⚖️ Official Leaderboard Tie-Breaking Rules
Rankings are determined deterministically using the following order:
1. **Total Forensic Score (PTS)** — *Highest rank first*
2. **Normal Golden Stars** — *Most stars cleared first*
3. **Mission Completion Status** — *Investigators that cleared the Boss Fortress rank above active participants*
4. **Total Elapsed Time** — *Faster completion time ranks higher*
5. **Timestamp of Final Solve** — *Earlier submission timestamp breaks ties*

---

## 🚀 Participant Checklist (How to Start)

1. Open the game link provided by the organizers.
2. Enter your **Investigator / Detective Alias** (e.g. `CyberViper` or your name) to register.
3. Save your unique **Personal Access Code** (e.g. `OJAS-9K3M4X7P`) so you can resume your session anytime.
4. Read the **Mission Briefing**, inspect the **3D World Map**, and begin with **Case 01** in Mushroom Village!
5. Keep an eye on the **Live Leaderboard** and good luck recovering the Golden Star!
