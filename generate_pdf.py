import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages after 1)
        if self._pageNumber > 1:
            self.drawString(36, 806, "MARIO: THE CYBER HEIST — TOURNAMENT REGULATIONS")
            self.drawRightString(559, 806, "CHANAKYA UNIVERSITY • OJAS 2026")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 800, 559, 800)

        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 40, 559, 40)
        self.drawString(36, 28, "OJAS Tech Fest 2026 • Cyber Incident Response Team (MK-CIRT)")
        self.drawRightString(559, 28, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_rules_pdf(output_path="MARIO_CTF_OFFICIAL_RULES_AND_GUIDE.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_dark = colors.HexColor("#0F172A")
    c_red = colors.HexColor("#DC2626")
    c_cyan = colors.HexColor("#0284C7")
    c_gold = colors.HexColor("#D97706")
    c_text = colors.HexColor("#1E293B")
    c_muted = colors.HexColor("#475569")
    c_bg_light = colors.HexColor("#F8FAFC")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_dark
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=c_red,
        textTransform='uppercase'
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_dark,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_text
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=c_text,
        leftIndent=14
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8.5,
        leading=11,
        textColor=c_dark
    )

    table_header_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_body_style = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark
    )

    table_bold_style = ParagraphStyle(
        'TDBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=c_dark
    )

    story = []

    # 1. Header Block
    header_data = [
        [
            Paragraph("MARIO: <font color='#DC2626'>THE CYBER HEIST</font>", title_style),
            Paragraph("CLASSIFICATION: <b>EYES ONLY</b><br/><font color='#DC2626'><b>THREAT LEVEL: OMEGA</b></font>", ParagraphStyle('MetaRight', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, alignment=2, textColor=c_muted))
        ],
        [
            Paragraph("CHANAKYA UNIVERSITY • OJAS TECH FEST 2026 • OFFICIAL CTF PARTICIPANT GUIDE", subtitle_style),
            ""
        ]
    ]
    t_head = Table(header_data, colWidths=[380, 143])
    t_head.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_head)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2.5, color=c_red, spaceAfter=8, spaceBefore=0))

    # 2. Mission Briefing Callout Box
    briefing_p = Paragraph(
        "<b>🚨 INCIDENT BRIEFING — OPERATION: RECOVER THE GOLDEN STAR</b><br/>"
        "At <b>03:14:07 AM</b>, the Mushroom Kingdom Master Sanctum vault security perimeter collapsed. The kingdom’s core power source, <b>THE GOLDEN STAR</b>, was exfiltrated by rogue cyber syndicate <b>'PHANTOM_SHROOM'</b>. As cyber operatives, your mission is to investigate compromised sectors on the <b>3D World Map</b>, analyze forensic evidence, bypass firewalls, defeat Bowser’s mainframe shields, and recover the Golden Star.",
        ParagraphStyle('Callout', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12.5, textColor=colors.HexColor("#0F172A"))
    )
    t_briefing = Table([[briefing_p]], colWidths=[523])
    t_briefing.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F9FF")),
        ('LINELEFT', (0,0), (0,0), 4, c_cyan),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_briefing)
    story.append(Spacer(1, 10))

    # 3. Sector Progression Table
    story.append(Paragraph("🗺️ 1. SECTOR PROGRESSION & FORENSIC WORKBENCHES", h1_style))
    story.append(Spacer(1, 4))
    
    sector_rows = [
        [
            Paragraph("SEC", table_header_style),
            Paragraph("SECTOR NAME", table_header_style),
            Paragraph("FORENSIC SPECIALIZATION & OBJECTIVES", table_header_style),
            Paragraph("GATING STATUS", table_header_style)
        ],
        [
            Paragraph("<b>01</b>", table_bold_style),
            Paragraph("<b>Mushroom Village</b>", table_bold_style),
            Paragraph("Exif metadata extraction, Wireshark PCAP packet analysis, Linux file permissions & SUID escalation.", table_body_style),
            Paragraph("<font color='#16A34A'><b>0 ⭐ Unlocked</b></font>", table_body_style)
        ],
        [
            Paragraph("<b>02</b>", table_bold_style),
            Paragraph("<b>Dark Forest</b>", table_bold_style),
            Paragraph("SQL Injection auth bypass, SHA-256 rainbow tables / password cracking, DOM XSS payload sanitization.", table_body_style),
            Paragraph("<font color='#D97706'><b>2 ⭐ Required</b></font>", table_body_style)
        ],
        [
            Paragraph("<b>03</b>", table_bold_style),
            Paragraph("<b>Haunted Mansion</b>", table_bold_style),
            Paragraph("Python bytecode decompilation, memory buffer overflow analysis, encrypted firmware string extraction.", table_body_style),
            Paragraph("<font color='#D97706'><b>5 ⭐ Required</b></font>", table_body_style)
        ],
        [
            Paragraph("<b>04</b>", table_bold_style),
            Paragraph("<b>Koopa HQ</b>", table_bold_style),
            Paragraph("JWT secret key forgery / privilege escalation, Insecure AWS S3 cloud bucket enumeration.", table_body_style),
            Paragraph("<font color='#D97706'><b>8 ⭐ Required</b></font>", table_body_style)
        ],
        [
            Paragraph("<b>05</b>", table_bold_style),
            Paragraph("<b>Final Fortress</b>", table_bold_style),
            Paragraph("<b>Boss Showdown:</b> Shatter 4 Sector Shields → Synthesize & Extract Master Champion Flag.", table_body_style),
            Paragraph("<font color='#DC2626'><b>11 ⭐ Required</b></font>", table_body_style)
        ]
    ]

    t_sectors = Table(sector_rows, colWidths=[32, 105, 296, 90])
    t_sectors.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_sectors)
    story.append(Spacer(1, 10))

    # 4. Scoring & Economy Grid
    story.append(Paragraph("🎮 2. SCORING SYSTEM & GAME ECONOMY", h1_style))
    story.append(Spacer(1, 4))

    eco_col1 = [
        Paragraph("<b>🏆 Forensic Points (Score)</b><br/>Every case cleared awards between <b>100 to 500 PTS</b> based on forensic complexity. Scores are registered atomically on the official server ledger.", body_style),
        Spacer(1, 6),
        Paragraph("<b>⭐ Golden Stars (0 - 12)</b><br/>Cases 1–11 award 1 Star each. Accumulate stars to dissolve quantum firewalls guarding higher sector islands. Clearing all 11 unlocks Bowser's Fortress.", body_style)
    ]
    eco_col2 = [
        Paragraph("<b>🪙 Cyber Coins & 3D ? Blocks</b><br/>Each investigator starts with <b>100 Cyber Coins</b>. Earn more by solving cases or clicking floating 3D Question Blocks on the map. Spend coins to decrypt hints!", body_style),
        Spacer(1, 6),
        Paragraph("<b>⏱️ Monotonic Competition Timer</b><br/>High-precision competition clock calibrated with server UTC. Automatically locks the exact millisecond the final Boss flag is verified.", body_style)
    ]

    t_eco = Table([[eco_col1, eco_col2]], colWidths=[256, 257])
    t_eco.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), c_bg_light),
        ('BACKGROUND', (1,0), (1,0), c_bg_light),
        ('BOX', (0,0), (0,0), 0.5, colors.HexColor("#E2E8F0")),
        ('BOX', (1,0), (1,0), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_eco)
    story.append(Spacer(1, 10))

    # 5. Solo Operative System
    story.append(Paragraph("👤 3. SOLO INVESTIGATOR SYSTEM & SESSION PORTABILITY", h1_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("• <b>Individual 1-vs-All Format:</b> Every participant competes independently on their personal laptop or workstation. No squads or team collaboration.", bullet_style))
    story.append(Paragraph("• <b>Personal Access Code:</b> When you register, you receive a unique cryptographic access code (e.g., <code>OJAS-W7KP-92RM</code>). Keep it safe!", bullet_style))
    story.append(Paragraph("• <b>Session Portability:</b> Resume your mission from any browser or workstation by entering your Access Code. Solves and coins are saved in real-time.", bullet_style))

    # Page Break to Page 2
    story.append(PageBreak())

    # PAGE 2: Rules, Prohibited Actions, Tie-Breaking & Checklist
    story.append(Paragraph("MARIO: <font color='#DC2626'>THE CYBER HEIST</font>", title_style))
    story.append(Paragraph("OFFICIAL TOURNAMENT RULES & CODE OF CONDUCT • REGULATION ID: CTF-REG-2026", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=c_dark, spaceAfter=10, spaceBefore=0))

    story.append(Paragraph("📜 4. OFFICIAL COMPETITION REGULATIONS", h1_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>1. Standard Flag Format:</b> All flags strictly adhere to the standardized structure: <code>FLAG{SAMPLE_FLAG_TEXT}</code>. Flags are strictly <b>case-sensitive</b> and must include the outer <code>FLAG{...}</code> wrapper.", bullet_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>2. Anti-Brute-Force Rate Limiting:</b> Automated dictionary attacks, fuzzing, or rapid scripted submissions against the flag submission box trigger automatic IP rate limiting (<b>maximum 10 attempts per 30 seconds</b>).", bullet_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>3. Hint Transparency Policy:</b> Unlocking forensic hints deducts Cyber Coins permanently from your individual treasury. Hints are progressive (Tier 1: Investigative Angle → Tier 2: Specific Vector).", bullet_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>4. Deterministic Podium Tie-Breaking:</b> Standings are ranked automatically without arbitrary manual overrides using this strict priority cascade:", bullet_style))
    
    tie_breaker_text = (
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>1. Total Forensic Points (Score)</b> — <i>Highest score ranks first</i><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>2. Normal Golden Stars Recovered</b> — <i>Most cases cleared ranks higher</i><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>3. Mission Completion Status</b> — <i>Investigators that breached the Boss Fortress rank above active participants</i><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>4. Total Elapsed Mission Time</b> — <i>Faster completion clock ranks higher</i><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>5. Timestamp of Final Solved Flag</b> — <i>Earlier server-recorded solve timestamp breaks final ties</i>"
    )
    story.append(Paragraph(tie_breaker_text, ParagraphStyle('TieSub', parent=body_style, leading=14)))
    story.append(Spacer(1, 10))

    # Prohibited Actions Warning Box
    warning_content = [
        Paragraph("<b>⚠️ PROHIBITED ACTIONS (ZERO TOLERANCE — IMMEDIATE DISQUALIFICATION)</b>", ParagraphStyle('WarnHead', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#991B1B"))),
        Spacer(1, 4),
        Paragraph("• <b>Infrastructure Attacks:</b> Do NOT launch Denial-of-Service (DoS/DDoS) floods, SQL injection against platform endpoints, or port scans against the host server. All challenge exploitation is strictly confined to individual case workbenches.", ParagraphStyle('WarnB', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11.5, textColor=colors.HexColor("#7F1D1D"))),
        Paragraph("• <b>Inter-Participant Collusion:</b> Sharing flags, private keys, solutions, or access codes with other participants is strictly prohibited. This is a 100% individual tournament.", ParagraphStyle('WarnB', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11.5, textColor=colors.HexColor("#7F1D1D"))),
        Paragraph("• <b>Account Hijacking:</b> Do NOT attempt to brute-force or use another participant's Access Code or session credentials.", ParagraphStyle('WarnB', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11.5, textColor=colors.HexColor("#7F1D1D")))
    ]
    t_warning = Table([[warning_content]], colWidths=[523])
    t_warning.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
        ('LINELEFT', (0,0), (0,0), 4, c_red),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#FECACA")),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_warning)
    story.append(Spacer(1, 10))

    # 5. Checklist Box
    story.append(Paragraph("🚀 5. OPERATIVE QUICKSTART CHECKLIST", h1_style))
    story.append(Spacer(1, 4))
    
    checklist_rows = [
        [Paragraph("☐", ParagraphStyle('Chk', fontName='Helvetica-Bold', fontSize=10, textColor=c_muted)), Paragraph("<b>Step 1 — Register Operative:</b> Open the tournament portal and enter your detective alias / name to register.", body_style)],
        [Paragraph("☐", ParagraphStyle('Chk', fontName='Helvetica-Bold', fontSize=10, textColor=c_muted)), Paragraph("<b>Step 2 — Save Access Code:</b> Keep your personal Access Code safe to resume your session from any device.", body_style)],
        [Paragraph("☐", ParagraphStyle('Chk', fontName='Helvetica-Bold', fontSize=10, textColor=c_muted)), Paragraph("<b>Step 3 — Inspect 3D Map:</b> Review the Mission Briefing and begin investigation in Sector 01 (Mushroom Village).", body_style)],
        [Paragraph("☐", ParagraphStyle('Chk', fontName='Helvetica-Bold', fontSize=10, textColor=c_muted)), Paragraph("<b>Step 4 — Breach Bowser's Fortress:</b> Accumulate 11 Golden Stars to unlock Sector 05 and defeat the final boss!", body_style)]
    ]
    t_check = Table(checklist_rows, colWidths=[20, 503])
    t_check.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_check)
    story.append(Spacer(1, 14))

    # Official Validation Stamp
    stamp_data = [
        [
            Paragraph("<b>TOURNAMENT AUTHORIZATION:</b><br/>OJAS 2026 ORGANIZING COMMITTEE<br/><font color='#64748B'>Chanakya University Cyber Security Directorate • Bangalore, India</font>", ParagraphStyle('StampL', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=10, textColor=c_dark)),
            Paragraph("<b>STATUS: VERIFIED & ACTIVE</b><br/>OFFICIAL COMPETITION BRIEFING<br/><font color='#64748B'>Chanakya University Tech Fest</font>", ParagraphStyle('StampR', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=10, alignment=2, textColor=c_dark))
        ]
    ]
    t_stamp = Table(stamp_data, colWidths=[300, 223])
    t_stamp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94A3B8")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_stamp)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully generated: {output_path}")

if __name__ == "__main__":
    build_rules_pdf()
