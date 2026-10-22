# Generates the official master solution and exploitation cheat sheet PDF for event hosts.

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class CheatSheetCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic total page numbering and running headers/footers."""
    def __init__(self, *args, **kwargs):
        super(CheatSheetCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(CheatSheetCanvas, self).showPage()
        super(CheatSheetCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#DC2626"))

        # Running Header (Top of each page)
        self.drawString(36, 808, "CONFIDENTIAL // HOST & ORGANIZER EYES ONLY")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawRightString(559, 808, "MARIO: THE CYBER HEIST — SOLUTION CHEAT SHEET")

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 802, 559, 802)

        # Running Footer (Bottom of each page)
        self.line(36, 36, 559, 36)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 24, "Chanakya University • OJAS Tech Fest 2026 • Master Answer Key & Exploitation Guide")
        self.drawRightString(559, 24, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_cheat_sheet_pdf(output_path="MARIO_CTF_SOLUTION_CHEAT_SHEET.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Brand Colors
    c_dark = colors.HexColor("#0F172A")
    c_red = colors.HexColor("#DC2626")
    c_cyan = colors.HexColor("#0284C7")
    c_green = colors.HexColor("#16A34A")
    c_gold = colors.HexColor("#D97706")
    c_text = colors.HexColor("#1E293B")
    c_muted = colors.HexColor("#475569")
    c_bg_light = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_dark
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=c_red,
        textTransform='uppercase'
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_dark,
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_text
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    table_header = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        textColor=colors.white
    )

    table_cell = ParagraphStyle(
        'TC',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=c_text
    )

    table_code = ParagraphStyle(
        'TCode',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=7,
        leading=8.5,
        textColor=c_dark
    )

    card_title = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=c_dark
    )

    card_meta = ParagraphStyle(
        'CardMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=c_cyan
    )

    why_label = ParagraphStyle(
        'WhyLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#7C2D12")
    )

    why_text = ParagraphStyle(
        'WhyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_text
    )

    how_label = ParagraphStyle(
        'HowLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#065F46")
    )

    how_text = ParagraphStyle(
        'HowText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_text
    )

    flag_box_style = ParagraphStyle(
        'FlagBox',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#047857")
    )

    story = []

    # ==========================================
    # 1. HEADER BANNER
    # ==========================================
    badge_p = Paragraph("⚠️ CONFIDENTIAL DOCUMENT // FACULTY & HOST EYE ONLY • DO NOT DISTRIBUTE TO PARTICIPANTS", subtitle_style)
    title_p = Paragraph("🍄 MARIO: THE CYBER HEIST — SOLUTION CHEAT SHEET", title_style)
    sub_p = Paragraph("<b>Chanakya University • OJAS Tech Fest 2026</b> | Complete Forensic Solutions, Vulnerability Explanations ('Why') & Exploitation Guides ('How to Crack')", body_style)

    header_table = Table(
        [
            [badge_p],
            [title_p],
            [sub_p]
        ],
        colWidths=[523]
    )
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#FCA5A5")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # Host Credentials Snapshot Bar
    creds_p = Paragraph(
        "<b>🔐 Host Terminal Access:</b> Navigate to <code>http://127.0.0.1:5000/admin</code> (or <code>/leaderboard</code>). "
        "<b>Passkeys:</b> <code>OJAS-HOST-ALPHA-7701</code> (Primary), <code>OJAS-HOST-BRAVO-9924</code> (Co-Host), "
        "<code>OJAS-HOST-SUPER-4418</code> (Superadmin). Emergency fallback: <code>OJAS_ADMIN_2026</code>.",
        body_style
    )
    creds_table = Table([[creds_p]], colWidths=[523])
    creds_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#93C5FD")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(creds_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # 2. MASTER QUICK-REFERENCE TABLE
    # ==========================================
    story.append(Paragraph("🎯 Master Quick-Reference Summary Table", h1_style))
    story.append(Paragraph("Quickly look up case numbers, categories, flags, and sector shield keywords for immediate reference during live rounds.", body_style))
    story.append(Spacer(1, 4))

    table_data = [
        [
            Paragraph("Case", table_header),
            Paragraph("Challenge Title", table_header),
            Paragraph("Sector", table_header),
            Paragraph("Category", table_header),
            Paragraph("Points", table_header),
            Paragraph("Exact Flag String", table_header),
            Paragraph("Shield Key", table_header),
        ],
        [
            Paragraph("<b>#1</b>", table_cell),
            Paragraph("The Broken Notice Board", table_cell),
            Paragraph("S1: Village", table_cell),
            Paragraph("Web / DOM", table_cell),
            Paragraph("100", table_cell),
            Paragraph("FLAG{MUSHROOM_SECRET_OJAS_2026}", table_code),
            Paragraph("<b>SECRET</b>", table_code),
        ],
        [
            Paragraph("<b>#2</b>", table_cell),
            Paragraph("The Suspicious Intercept", table_cell),
            Paragraph("S1: Village", table_cell),
            Paragraph("Cryptography", table_cell),
            Paragraph("150", table_cell),
            Paragraph("FLAG{LETTER_CIPHER_SOLVED_OJAS}", table_code),
            Paragraph("—", table_cell),
        ],
        [
            Paragraph("<b>#3</b>", table_cell),
            Paragraph("Deep Glitch in the Pines", table_cell),
            Paragraph("S2: Forest", table_cell),
            Paragraph("Steganography", table_cell),
            Paragraph("200", table_cell),
            Paragraph("FLAG{FOREST_PIXEL_STEGO_OJAS}", table_code),
            Paragraph("<b>PINES</b>", table_code),
        ],
        [
            Paragraph("<b>#4</b>", table_cell),
            Paragraph("The Shadow Metadata Trail", table_cell),
            Paragraph("S2: Forest", table_cell),
            Paragraph("OSINT / EXIF", table_cell),
            Paragraph("200", table_cell),
            Paragraph("FLAG{METADATA_TRAIL_REVEALED_OJAS}", table_code),
            Paragraph("—", table_cell),
        ],
        [
            Paragraph("<b>#5</b>", table_cell),
            Paragraph("Corrupted Proxy Stream", table_cell),
            Paragraph("S2: Forest", table_cell),
            Paragraph("Net Forensics", table_cell),
            Paragraph("250", table_cell),
            Paragraph("FLAG{DARK_FOREST_STREAM_DECODED}", table_code),
            Paragraph("—", table_cell),
        ],
        [
            Paragraph("<b>#6</b>", table_cell),
            Paragraph("Phantom Directory Traversal", table_cell),
            Paragraph("S3: Mansion", table_cell),
            Paragraph("Web Security", table_cell),
            Paragraph("250", table_cell),
            Paragraph("FLAG{BOO_GHOST_PATH_DISCOVERED}", table_code),
            Paragraph("—", table_cell),
        ],
        [
            Paragraph("<b>#7</b>", table_cell),
            Paragraph("Boo's Vault IDOR Manipulation", table_cell),
            Paragraph("S3: Mansion", table_cell),
            Paragraph("API Security", table_cell),
            Paragraph("300", table_cell),
            Paragraph("FLAG{API_AUTH_BYPASS_OJAS}", table_code),
            Paragraph("<b>BOO</b>", table_code),
        ],
        [
            Paragraph("<b>#8</b>", table_cell),
            Paragraph("Poltergeist Session Forgery", table_cell),
            Paragraph("S3: Mansion", table_cell),
            Paragraph("JWT Token", table_cell),
            Paragraph("300", table_cell),
            Paragraph("FLAG{SESSION_FORGERY_DETECTED_OJAS}", table_code),
            Paragraph("—", table_cell),
        ],
        [
            Paragraph("<b>#9</b>", table_cell),
            Paragraph("The Framed Shellshock Recon", table_cell),
            Paragraph("S4: Koopa HQ", table_cell),
            Paragraph("Host Forensics", table_cell),
            Paragraph("350", table_cell),
            Paragraph("FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}", table_code),
            Paragraph("—", table_cell),
        ],
        [
            Paragraph("<b>#10</b>", table_cell),
            Paragraph("Correlated SIEM Log Breaches", table_cell),
            Paragraph("S4: Koopa HQ", table_cell),
            Paragraph("Threat Hunting", table_cell),
            Paragraph("350", table_cell),
            Paragraph("FLAG{CORRELATED_LOGS_INSIDER_OJAS}", table_code),
            Paragraph("<b>INSIDER</b>", table_code),
        ],
        [
            Paragraph("<b>#11</b>", table_cell),
            Paragraph("Fortress Mainframe SQLi", table_cell),
            Paragraph("S4: Koopa HQ", table_cell),
            Paragraph("SQL Injection", table_cell),
            Paragraph("400", table_cell),
            Paragraph("FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}", table_code),
            Paragraph("—", table_cell),
        ],
        [
            Paragraph("<b>#12</b>", table_cell),
            Paragraph("Mecha-Shellshock Showdown", table_cell),
            Paragraph("S5: Fortress", table_cell),
            Paragraph("Master Boss", table_cell),
            Paragraph("500", table_cell),
            Paragraph("FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}", table_code),
            Paragraph("<b>4 KEYS</b>", table_code),
        ],
    ]

    summary_table = Table(table_data, colWidths=[24, 115, 55, 65, 30, 184, 50])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_dark),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (4, 0), (4, -1), 'CENTER'),
        ('ALIGN', (6, 0), (6, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # 3. DETAILED CASE-BY-CASE BREAKDOWN (WHY & HOW)
    # ==========================================
    story.append(Paragraph("🔬 Case-by-Case Deep Dive: 'Why' (Vulnerability) & 'How to Crack' (Exploit Walkthrough)", h1_style))
    story.append(Paragraph("Each case is categorized with technical rationale explaining the vulnerability class, along with the precise tactical steps required to solve it.", body_style))
    story.append(Spacer(1, 6))

    cases_data = [
        {
            "id": 1,
            "title": "The Broken Notice Board",
            "sector": "Sector 01: Mushroom Village (Ground Zero)",
            "cat": "Web Security & Client DOM Forensics",
            "pts": "100 PTS | +1 ⭐ | +50 🪙",
            "flag": "FLAG{MUSHROOM_SECRET_OJAS_2026}",
            "boss_key": "SECRET",
            "why": "<b>Insecure Information Disclosure in Source Comments (CWE-615):</b> Developers routinely leave staging tokens, comments, and debug values inside client-facing HTML. Because the browser downloads the raw HTML markup before rendering, comments (<code>&lt;!-- ... --&gt;</code>) are never executed as logic but remain completely readable by anyone inspecting the DOM.",
            "how": "<b>1.</b> In the challenge workbench, click <b>[ TOGGLE DOM TREE INSPECTOR ]</b> (or press F12 in standard dev tools).<br/><b>2.</b> Inspect the HTML structure inside container <code>#village-bulletin-board</code>.<br/><b>3.</b> Locate line 94: <code>&lt;!-- cyber-heist-token: FLAG{MUSHROOM_SECRET_OJAS_2026} --&gt;</code>.<br/><b>4.</b> Note the sector keyword <b>SECRET</b> for the World 5 Boss Shield."
        },
        {
            "id": 2,
            "title": "The Suspicious Intercept",
            "sector": "Sector 01: Mushroom Village (Ground Zero)",
            "cat": "Classical Cryptography (Monoalphabetic Substitution)",
            "pts": "150 PTS | +1 ⭐ | +75 🪙",
            "flag": "FLAG{LETTER_CIPHER_SOLVED_OJAS}",
            "boss_key": None,
            "why": "<b>Weak Obfuscation / Insecure Classical Cipher (CWE-327):</b> The adversary intercepted traffic and attempted to hide intelligence using ROT-13 (Caesar shift by 13). ROT-13 offers zero cryptographic entropy because the key space is fixed ($k=13$). Modern forensics easily breaks substitution ciphers by observing the known-plaintext prefix <code>SYNT</code> -> <code>FLAG</code>.",
            "how": "<b>1.</b> Observe the ciphertext: <code>SYNT{YRGGRE_PVCURE_FBYIRQ_BWNF}</code>.<br/><b>2.</b> Calculate the alphabet distance between 'S' and 'F' ($19 - 6 = 13$ mod 26).<br/><b>3.</b> In the interactive decoder workbench, drag the <b>CAESAR ROTATION SHIFT</b> slider to <b>13</b>.<br/><b>4.</b> The deciphered text instantly turns bright green: <code>FLAG{LETTER_CIPHER_SOLVED_OJAS}</code>."
        },
        {
            "id": 3,
            "title": "Deep Glitch in the Pines",
            "sector": "Sector 02: Dark Forest (Digital Woods • Requires 2 ⭐)",
            "cat": "Steganography & LSB Bitplane Concealment",
            "pts": "200 PTS | +1 ⭐ | +100 🪙",
            "flag": "FLAG{FOREST_PIXEL_STEGO_OJAS}",
            "boss_key": "PINES",
            "why": "<b>Least Significant Bit (LSB) Steganography:</b> Digital images store color as 8-bit values per channel (0–255). Modifying only the lowest bit (Bit 0) alters the RGB color by a mere $1/256$, which is imperceptible to the human eye. Attackers exploit this perceptual threshold to conceal binary ASCII streams inside high-resolution raster images.",
            "how": "<b>1.</b> Open the drone surveillance viewer in Case 3.<br/><b>2.</b> Toggle through the bitplane filter buttons located underneath the image canvas.<br/><b>3.</b> Click <b>[ GREEN PLANE ]</b> or <b>[ LSB BITPLANE 0 ]</b>.<br/><b>4.</b> The image contrast strips away high-order pixels, exposing the hidden fluorescent ASCII text: <code>BITPLANE 0 CONCEALED: FLAG{FOREST_PIXEL_STEGO_OJAS}</code>.<br/><b>5.</b> Note the sector keyword <b>PINES</b> for Boss Shield 2."
        },
        {
            "id": 4,
            "title": "The Shadow Metadata Trail",
            "sector": "Sector 02: Dark Forest (Digital Woods • Requires 2 ⭐)",
            "cat": "OSINT & Forensic Artifact Analysis (EXIF)",
            "pts": "200 PTS | +1 ⭐ | +100 🪙",
            "flag": "FLAG{METADATA_TRAIL_REVEALED_OJAS}",
            "boss_key": None,
            "why": "<b>File Header & Metadata Information Leakage (CWE-200):</b> Modern media standards (JPEG, TIFF, PDF) append rich technical metadata headers (EXIF, IPTC, XMP) containing timestamps, camera sensor models, GPS coordinates, and user comments. Failing to scrub EXIF tags during file export leaves an indelible forensic breadcrumb trail.",
            "how": "<b>1.</b> In Case 4, inspect the <b>RAW EXIF METADATA TERMINAL</b>.<br/><b>2.</b> Scroll through standard EXIF tags (Aperture, ShutterSpeed, FocalLength).<br/><b>3.</b> Examine the bottom vendor tags: <code>Software: CyberHeist_Stealth_Encoder</code> and <code>UserComment: FLAG{METADATA_TRAIL_REVEALED_OJAS}</code>.<br/><b>4.</b> Copy the flag directly from the comment field."
        },
        {
            "id": 5,
            "title": "Corrupted Proxy Stream",
            "sector": "Sector 02: Dark Forest (Digital Woods • Requires 2 ⭐)",
            "cat": "Network Protocol & Packet Stream Hexdump Analysis",
            "pts": "250 PTS | +1 ⭐ | +125 🪙",
            "flag": "FLAG{DARK_FOREST_STREAM_DECODED}",
            "boss_key": None,
            "why": "<b>Cleartext Network Transmission (CWE-319):</b> The rogue proxy intercepted an outgoing TCP socket stream without TLS/SSL encryption. Even though presented as raw hex bytes, cleartext traffic payloads retain direct 1-to-1 ASCII character equivalence, allowing network analysts to reconstruct protocol payloads via hexadecimal decoding.",
            "how": "<b>1.</b> Inspect the captured raw hex dump: <code>46 4c 41 47 7b 44 41 52 4b 5f 46 4f 52 45 53 54 ... 7d</code>.<br/><b>2.</b> Recognize the standard ASCII prefix: $0x46 = 'F', 0x4C = 'L', 0x41 = 'A', 0x47 = 'G', 0x7B = '\{'$.<br/><b>3.</b> Convert the 32 hex pairs into ASCII using the built-in workbench decoder or Python <code>bytes.fromhex(...)</code>.<br/><b>4.</b> Output yields: <code>FLAG{DARK_FOREST_STREAM_DECODED}</code>."
        },
        {
            "id": 6,
            "title": "Phantom Directory Traversal",
            "sector": "Sector 03: Haunted Mansion (Phantom Network • Requires 5 ⭐)",
            "cat": "Web Security: Information Disclosure & Path Traversal",
            "pts": "250 PTS | +1 ⭐ | +125 🪙",
            "flag": "FLAG{BOO_GHOST_PATH_DISCOVERED}",
            "boss_key": None,
            "why": "<b>Predictable Resource Location & Disclosed Sensitive Endpoints (CWE-538):</b> Web administrators frequently attempt 'security through obscurity' by adding hidden directories to <code>robots.txt</code> to stop search crawlers. Attackers actively read <code>robots.txt</code> to locate sensitive backup archives (<code>.bak</code>), which are often hosted with improper directory traversal access controls.",
            "how": "<b>1.</b> In the Mansion File Explorer, type path <code>/robots.txt</code> and click <b>FETCH</b>.<br/><b>2.</b> Read the crawler directive: <code>Disallow: /secret_attic/ # Note: ghost_manifesto.bak contains sector vault key</code>.<br/><b>3.</b> Change the input path to <code>/secret_attic/ghost_manifesto.bak</code> and click <b>FETCH</b>.<br/><b>4.</b> The server returns the leaked backup document displaying: <code>FLAG{BOO_GHOST_PATH_DISCOVERED}</code>."
        },
        {
            "id": 7,
            "title": "Boo's Vault IDOR Manipulation",
            "sector": "Sector 03: Haunted Mansion (Phantom Network • Requires 5 ⭐)",
            "cat": "API Security: Broken Object Level Authorization (IDOR)",
            "pts": "300 PTS | +1 ⭐ | +150 🪙",
            "flag": "FLAG{API_AUTH_BYPASS_OJAS}",
            "boss_key": "BOO",
            "why": "<b>Insecure Direct Object Reference / BOLA (OWASP API1):</b> The REST API endpoint accepts an object ID directly from the client request (<code>locker_id</code>) and an access-tier header (<code>X-Access-Level</code>). Because the backend fails to validate whether the authenticated session actually owns locker #0001, an attacker simply swaps the ID to access unauthorized data.",
            "how": "<b>1.</b> Observe the default client parameters: Guest locker is <code>1042</code> with header <code>X-Access-Level: guest_phantom</code>.<br/><b>2.</b> Modify parameter <code>locker_id</code> to VIP vault <b>1</b>.<br/><b>3.</b> Modify the HTTP header to <code>X-Access-Level: master_phantom</code>.<br/><b>4.</b> Click <b>[ SEND INTERCEPTED API REQUEST ]</b>.<br/><b>5.</b> King Boo's Vault #0001 opens, releasing: <code>FLAG{API_AUTH_BYPASS_OJAS}</code>.<br/><b>6.</b> Note the sector keyword <b>BOO</b> for Boss Shield 3."
        },
        {
            "id": 8,
            "title": "Poltergeist Session Forgery",
            "sector": "Sector 03: Haunted Mansion (Phantom Network • Requires 5 ⭐)",
            "cat": "Token Exploitation: JWT Algorithm Confusion (None Alg)",
            "pts": "300 PTS | +1 ⭐ | +150 🪙",
            "flag": "FLAG{SESSION_FORGERY_DETECTED_OJAS}",
            "boss_key": None,
            "why": "<b>JWT 'alg: none' Signature Verification Bypass (CWE-347):</b> JSON Web Tokens rely on the header <code>\"alg\"</code> field to determine how to verify signatures. In insecure implementations, setting <code>\"alg\": \"none\"</code> triggers the server to treat the token as unsigned, accepting arbitrary tampering in the payload (elevating <code>role: guest</code> to <code>role: admin</code>) without verifying any cryptographic signature.",
            "how": "<b>1.</b> In the JWT Token Forge workbench, switch <b>TOKEN ROLE</b> to <b>admin</b>.<br/><b>2.</b> Switch <b>SIGNATURE ALGORITHM (alg)</b> from <code>HS256 (Signed)</code> to <b>none (Unsigned Bypass)</b>.<br/><b>3.</b> Notice the signature hash is stripped: <code>eyJhbGciOiJub25lIn0... .</code>.<br/><b>4.</b> Click <b>[ TRANSMIT FORGED SESSION COOKIE ]</b>.<br/><b>5.</b> The server accepts the forged admin cookie and unlocks: <code>FLAG{SESSION_FORGERY_DETECTED_OJAS}</code>."
        },
        {
            "id": 9,
            "title": "The Framed Shellshock Recon",
            "sector": "Sector 04: Koopa HQ (Industrial Bastion • Requires 8 ⭐)",
            "cat": "Operating System & Host Artifact Forensics",
            "pts": "350 PTS | +1 ⭐ | +175 🪙",
            "flag": "FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}",
            "boss_key": None,
            "why": "<b>Persistence Backdoor & Log Evasion Analysis:</b> Adversaries who compromise Linux environments often implant persistence hooks inside user shell termination and profile scripts (e.g., <code>~/.bash_logout</code>, <code>~/.profile</code>). Inspecting these hidden files reveals command-and-control communication strings and forensic evidence proving Shellshock was framed.",
            "how": "<b>1.</b> In Case 9, run forensic investigation on the compromised Koopa host.<br/><b>2.</b> Inspect the contents of <code>cat /home/shellshock/.bash_logout.bak</code>.<br/><b>3.</b> Locate the embedded reverse shell payload timestamped 48 hours prior to the heist.<br/><b>4.</b> Extract the token string: <code>FLAG{SHELLSHOCK_WAS_FRAMED_OJAS}</code>."
        },
        {
            "id": 10,
            "title": "Correlated SIEM Log Breaches",
            "sector": "Sector 04: Koopa HQ (Industrial Bastion • Requires 8 ⭐)",
            "cat": "Threat Hunting & Log Correlation Analysis",
            "pts": "350 PTS | +1 ⭐ | +175 🪙",
            "flag": "FLAG{CORRELATED_LOGS_INSIDER_OJAS}",
            "boss_key": "INSIDER",
            "why": "<b>Anomalous User-Agent & Query Correlation (MITRE ATT&CK T1071):</b> Massive SIEM access logs conceal attacks inside high-volume noise. Threat hunters filter out 401/403/404 noise and isolate pivot IP addresses (<code>10.99.13.37</code>). Attackers using bespoke scripts frequently broadcast identifiable User-Agent strings and exploit parameters in the access stream.",
            "how": "<b>1.</b> In the SIEM analyzer, apply the filter: <code>IP=10.99.13.37 AND STATUS=200</code>.<br/><b>2.</b> Review the correlated HTTP GET requests hitting <code>/internal/admin/override</code>.<br/><b>3.</b> Inspect the User-Agent header: <code>User-Agent: Insider-Infiltrator/1.0 (FlagPayload: FLAG{CORRELATED_LOGS_INSIDER_OJAS})</code>.<br/><b>4.</b> Note the threat tag parameter <b>INSIDER</b> for Boss Shield 4."
        },
        {
            "id": 11,
            "title": "Koopa Fortress Mainframe Bypass",
            "sector": "Sector 04: Koopa HQ (Industrial Bastion • Requires 8 ⭐)",
            "cat": "Database Exploitation: SQL Injection (SQLi Tautology)",
            "pts": "400 PTS | +1 ⭐ | +200 🪙",
            "flag": "FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}",
            "boss_key": None,
            "why": "<b>Classic SQL Injection via Dynamic Query Concatenation (CWE-89):</b> The application constructs backend database queries via raw string interpolation: <code>SELECT * FROM employees WHERE badge_id = '{input}'</code>. Injecting a boolean tautology (<code>' OR '1'='1</code>) alters the AST syntax so the WHERE clause evaluates to true for every single row in the database table.",
            "how": "<b>1.</b> In the Koopa Security Badge terminal, enter the standard bypass tautology: <b>' OR '1'='1</b> (or <code>' OR 1=1 --</code>).<br/><b>2.</b> Click <b>[ QUERY DB ]</b>.<br/><b>3.</b> The database evaluates the condition as universally true, dumping all employee records.<br/><b>4.</b> Root admin record #999 reveals the archive token: <code>FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}</code>."
        },
        {
            "id": 12,
            "title": "Mecha-Shellshock Showdown (Master Core)",
            "sector": "Sector 05: Final Fortress (Master Vault • Requires 11 ⭐)",
            "cat": "Master Forensic Synthesis & 3D Boss Battle",
            "pts": "500 PTS | +2 ⭐ | +300 🪙",
            "flag": "FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}",
            "boss_key": "ALL 4 KEYS",
            "why": "<b>Multi-Vector Cryptographic Defense Synthesis:</b> The Final Boss represents an integrated defense-in-depth perimeter. Its quantum shields cannot be bypassed with brute force; they require reconstructing the 4 intelligence keywords collected across the previous 4 sectors: DOM comment keyword, stego ridge name, VIP vault owner, and internal threat tag.",
            "how": "<b>1.</b> Overcome Shield 1 (Sector 01 Keyword): <b>SECRET</b><br/><b>2.</b> Overcome Shield 2 (Sector 02 Keyword): <b>PINES</b><br/><b>3.</b> Overcome Shield 3 (Sector 03 Keyword): <b>BOO</b><br/><b>4.</b> Overcome Shield 4 (Sector 04 Keyword): <b>INSIDER</b><br/><b>5.</b> Neutralizing Shield 4 causes Mecha-Shellshock to collapse in 3D, unlocking the vault and <b>automatically displaying the Master Flag</b>: <code>FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}</code>.<br/><b>6.</b> Submit the Master Flag to freeze the competition clock and win the tournament!"
        }
    ]

    for c in cases_data:
        # Build individual case card
        header_text = f"<b>Case #{c['id']}: {c['title']}</b> &nbsp;|&nbsp; <i>{c['sector']}</i>"
        header_p = Paragraph(header_text, card_title)
        meta_p = Paragraph(f"<b>Category:</b> {c['cat']} &nbsp;•&nbsp; <b>Reward:</b> {c['pts']}", card_meta)

        flag_content = f"<b>EXACT FLAG:</b> <code>{c['flag']}</code>"
        if c.get("boss_key"):
            flag_content += f" &nbsp;&nbsp;|&nbsp;&nbsp; <b>BOSS SHIELD KEY:</b> <font color='#DC2626'><b>{c['boss_key']}</b></font>"
        flag_p = Paragraph(flag_content, flag_box_style)

        why_p = Paragraph(f"<b>WHY (Vulnerability Analysis):</b> {c['why']}", why_text)
        how_p = Paragraph(f"<b>HOW TO CRACK (Exploitation Steps):</b> {c['how']}", how_text)

        case_card_content = [
            [header_p],
            [meta_p],
            [flag_p],
            [why_p],
            [how_p]
        ]

        card_table = Table(case_card_content, colWidths=[523])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.75, c_border),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor("#ECFDF5")),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, c_border),
            ('LINEBELOW', (0, 1), (-1, 1), 0.5, c_border),
            ('LINEBELOW', (0, 2), (-1, 2), 0.5, colors.HexColor("#A7F3D0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(card_table)
        story.append(Spacer(1, 5))

    # ==========================================
    # 4. HOST OPERATIONS & TROUBLESHOOTING CHEAT SHEET
    # ==========================================
    story.append(Spacer(1, 6))
    story.append(Paragraph("🛠️ Host Live Operations & Troubleshooting Quick-Guide", h1_style))

    host_ops_data = [
        [
            Paragraph("<b>Scenario</b>", table_header),
            Paragraph("<b>Host Resolution / Action</b>", table_header)
        ],
        [
            Paragraph("<b>Participant Forgot Access Code</b>", table_cell),
            Paragraph("Open <code>/admin</code> -> Tab 1. Locate student row. The chip <code>OJAS-XXXXXX 📋</code> can be clicked to copy their code. Alternatively, students can resume directly using their registered <b>Register Number / USN</b> on the briefing screen.", table_cell)
        ],
        [
            Paragraph("<b>Participant Stuck on Boss Battle</b>", table_cell),
            Paragraph("Confirm they entered the 4 sector shield keywords: <code>SECRET</code> (Case 1), <code>PINES</code> (Case 3), <code>BOO</code> (Case 7), <code>INSIDER</code> (Case 10). Neutralizing all 4 triggers automatic flag reveal.", table_cell)
        ],
        [
            Paragraph("<b>Student Accidentally Concluded Mission Early</b>", table_cell),
            Paragraph("Direct the student to <code>/end</code> (Debrief page). They can click <b>'🔄 REOPEN / RESUME MISSION'</b> to unfreeze their timer and continue playing where they left off.", table_cell)
        ],
        [
            Paragraph("<b>Live Leaderboard Inspection</b>", table_cell),
            Paragraph("Leaderboard is strictly restricted to hosts at <code>/leaderboard</code>. Enter any Host Passkey (<code>OJAS-HOST-ALPHA-7701</code>) to view rankings sorted by Score DESC -> Stars DESC -> Time ASC.", table_cell)
        ],
        [
            Paragraph("<b>Reset Competition to Factory Clean State</b>", table_cell),
            Paragraph("In <code>/admin</code> -> Tab 4, click <b>'⚠️ FACTORY RESET CTF DATABASE'</b> (or call <code>admin_reset_system()</code>). Wipes all test squads and resets the competition state to LOBBY with 0 teams.", table_cell)
        ]
    ]

    host_table = Table(host_ops_data, colWidths=[160, 363])
    host_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_dark),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(host_table)

    # Build the document using the NumberedCanvas
    doc.build(story, canvasmaker=CheatSheetCanvas)
    print(f"[+] Successfully generated Cheat Sheet PDF: {output_path}")


if __name__ == "__main__":
    build_cheat_sheet_pdf()
