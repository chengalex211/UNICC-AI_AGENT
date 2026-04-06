"""
frontend_api/pdf_renderer.py
────────────────────────────
ReportLab PDF generator for CouncilReport dicts.
Extracted from main.py to keep route handlers thin.
"""
from __future__ import annotations

import io
import re


def report_to_pdf(r: dict) -> bytes:
    """Generate a structured PDF from a CouncilReport dict. Returns raw bytes."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether,
    )
    from reportlab.lib.enums import TA_CENTER  # noqa: F401  (used in footer)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=22*mm, bottomMargin=22*mm,
    )

    # ── palette ───────────────────────────────────────────────────────────────
    BLUE   = colors.HexColor("#007AFF")
    GREEN  = colors.HexColor("#34C759")
    ORANGE = colors.HexColor("#FF9500")
    RED    = colors.HexColor("#FF3B30")
    GRAY1  = colors.HexColor("#1C1C1E")
    GRAY3  = colors.HexColor("#48484A")
    GRAY5  = colors.HexColor("#8E8E93")
    GRAY6  = colors.HexColor("#F2F2F7")

    def decision_color(rec: str) -> object:
        rec = (rec or "").upper()
        if rec == "APPROVE": return GREEN
        if rec == "REJECT":  return RED
        return ORANGE

    base = getSampleStyleSheet()

    def S(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    cover_title  = S("CoverTitle",  fontSize=22, textColor=BLUE,  spaceAfter=4, fontName="Helvetica-Bold")
    cover_sub    = S("CoverSub",    fontSize=11, textColor=GRAY3, spaceAfter=2)
    cover_meta   = S("CoverMeta",   fontSize=9,  textColor=GRAY5, spaceAfter=2)
    h1_style     = S("H1",          fontSize=13, textColor=GRAY1, spaceBefore=10, spaceAfter=4, fontName="Helvetica-Bold")
    h2_style     = S("H2",          fontSize=11, textColor=BLUE,  spaceBefore=8,  spaceAfter=3, fontName="Helvetica-Bold")
    h3_style     = S("H3",          fontSize=10, textColor=GRAY3, spaceBefore=6,  spaceAfter=2, fontName="Helvetica-Bold")
    body_style   = S("Body",        fontSize=9,  textColor=GRAY3, spaceAfter=3,   leading=14)
    small_style  = S("Small",       fontSize=8,  textColor=GRAY5, spaceAfter=2,   leading=12)
    bullet_style = S("Bullet",      fontSize=9,  textColor=GRAY3, spaceAfter=2,   leftIndent=10, leading=13)
    label_style  = S("Label",       fontSize=8,  textColor=GRAY5, spaceAfter=1,   fontName="Helvetica-Bold", textTransform="uppercase")
    code_style   = S("Code",        fontSize=8,  textColor=GRAY3, fontName="Courier", spaceAfter=2, leading=12)

    def hr(): return HRFlowable(width="100%", thickness=0.5, color=GRAY6, spaceAfter=4, spaceBefore=4)
    def sp(h=4): return Spacer(1, h*mm)

    def safe(txt: str, max_chars: int = 2000) -> str:
        if not txt: return ""
        txt = str(txt)[:max_chars]
        return txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def parse_finding(f: str):
        """Return dict with risk/evidence/impact/score or None if not tagged."""
        if "[RISK]" not in f or "[EVIDENCE]" not in f:
            return None
        def extract(tag, nxt):
            m = re.search(rf'\[{tag}\]\s*(.*?)(?=\[{nxt}\]|$)', f, re.S)
            return (m.group(1) or "").strip() if m else ""
        return {
            "risk":     extract("RISK",     "EVIDENCE"),
            "evidence": extract("EVIDENCE", "IMPACT"),
            "impact":   extract("IMPACT",   "SCORE"),
            "score":    extract("SCORE",    r"\Z"),
        }

    def render_findings(block, findings):
        block.append(Paragraph("Key Findings", label_style))
        for idx, f in enumerate(findings[:8]):
            parsed = parse_finding(str(f))
            if parsed:
                sev_col = RED if "[CRITICAL]" in f.upper() or "critical" in f.lower() else ORANGE
                block.append(Paragraph(
                    f'<font color="{sev_col.hexval()}"><b>Finding {idx+1}</b></font>',
                    S(f"FH{idx}", fontSize=9, textColor=GRAY1, fontName="Helvetica-Bold",
                      spaceBefore=4, spaceAfter=1)))
                rows = []
                for tag, val in [("RISK", parsed["risk"]), ("EVIDENCE", parsed["evidence"]),
                                  ("IMPACT", parsed["impact"]), ("SCORE", parsed["score"])]:
                    if val:
                        rows.append([
                            Paragraph(f"<b>{tag}</b>",
                                      S(f"Tag{idx}{tag}", fontSize=7, textColor=GRAY5,
                                        fontName="Helvetica-Bold")),
                            Paragraph(safe(val, 300),
                                      S(f"Val{idx}{tag}", fontSize=8, textColor=GRAY3, leading=12)),
                        ])
                if rows:
                    t = Table(rows, colWidths=["15%", "85%"],
                              style=TableStyle([
                                  ("BACKGROUND", (0, 0), (-1, -1), GRAY6),
                                  ("TOPPADDING",    (0, 0), (-1, -1), 2),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                                  ("LEFTPADDING",   (0, 0), (-1, -1), 5),
                                  ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.white),
                              ]))
                    block.append(t)
                    block.append(sp(1))
            else:
                block.append(Paragraph(f"• {safe(str(f), 400)}", bullet_style))
        block.append(sp(2))

    def render_attack_trail(block, er):
        attack_trace   = er.get("attack_trace")  or []
        probe_trace    = er.get("probe_trace")    or []
        boundary_trace = er.get("boundary_trace") or []
        breach_details = er.get("breach_details") or []
        std_suite      = (er.get("standard_suite_results") or {}).get("all_results") or []

        if not attack_trace:
            return

        block.append(Paragraph("Live Attack Trail", label_style))
        block.append(sp(1))

        breaches = sum(1 for t in attack_trace if (t.get("classification") or "") == "BREACH")
        rows = [
            [Paragraph("Phase", small_style), Paragraph("Turns", small_style),
             Paragraph("Breaches", small_style)],
            [Paragraph("Phase 1 — Probe",    small_style), Paragraph(str(len(probe_trace)),    small_style), Paragraph("—", small_style)],
            [Paragraph("Phase 2 — Boundary", small_style), Paragraph(str(len(boundary_trace)), small_style), Paragraph("—", small_style)],
            [Paragraph("Phase 3 — Attack",   small_style), Paragraph(str(len(attack_trace)),   small_style),
             Paragraph(f'<font color="{RED.hexval() if breaches else GREEN.hexval()}"><b>{breaches}</b></font>', small_style)],
            [Paragraph("Standard Suite",     small_style), Paragraph(str(len(std_suite)),       small_style), Paragraph("—", small_style)],
        ]
        t = Table(rows, colWidths=["50%", "25%", "25%"],
                  style=TableStyle([
                      ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                      ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
                      ("BACKGROUND", (0, 1), (-1, -1), GRAY6),
                      ("TOPPADDING",    (0, 0), (-1, -1), 3),
                      ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                      ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                      ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.white),
                  ]))
        block.append(t)
        block.append(sp(2))

        if breach_details:
            block.append(Paragraph("Breach Records", label_style))
            for bd in breach_details[:6]:
                sev   = (bd.get("severity") or "HIGH").upper()
                sev_c = RED if sev == "CRITICAL" else ORANGE
                tid   = safe(bd.get("technique_id", ""), 30)
                tname = safe(bd.get("technique_name", ""), 60)
                turn  = bd.get("turn", "?")
                vec   = safe(bd.get("attack_vector", ""), 200)
                btype = safe(bd.get("breach_type", ""), 40).replace("_", " ")
                atk   = safe(bd.get("attack_message_excerpt", ""), 180)
                resp  = safe(bd.get("response_excerpt", ""), 180)

                brows = [
                    [Paragraph(f'<font color="{sev_c.hexval()}"><b>{sev} — {tid}: {tname}</b></font> (Turn {turn})',
                               S(f"BH{turn}", fontSize=8, textColor=GRAY1, fontName="Helvetica-Bold"))],
                ]
                for lbl, val in [("Attack Vector", vec), ("Breach Type", btype),
                                  ("Attack Message", atk), ("Target Response", resp)]:
                    if val:
                        brows.append([Paragraph(
                            f'<b>{lbl}:</b> <font color="{GRAY3.hexval()}">{val}</font>',
                            S(f"BR{turn}{lbl}", fontSize=7, textColor=GRAY3, leading=11))])

                bt = Table(brows, colWidths=["100%"],
                           style=TableStyle([
                               ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFF3F3")),
                               ("BACKGROUND", (0, 1), (-1, -1), GRAY6),
                               ("TOPPADDING",    (0, 0), (-1, -1), 3),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                               ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                               ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.white),
                           ]))
                block.append(bt)
                block.append(sp(1))

        if attack_trace:
            block.append(Paragraph("Phase 3 — Attack Timeline", label_style))
            hdr = [Paragraph(h, S(f"ATH{h}", fontSize=7, textColor=colors.white, fontName="Helvetica-Bold"))
                   for h in ["Turn", "Technique", "Classification", "Score"]]
            atrows = [hdr]
            for at in attack_trace[:20]:
                cls   = (at.get("classification") or "").upper()
                cls_c = RED if cls == "BREACH" else (ORANGE if cls == "SAFE_FAILURE" else GREEN)
                atrows.append([
                    Paragraph(str(at.get("turn", "")),              small_style),
                    Paragraph(safe(at.get("technique_id", ""), 30), code_style),
                    Paragraph(f'<font color="{cls_c.hexval()}"><b>{cls}</b></font>', small_style),
                    Paragraph(str(at.get("score", "")),              small_style),
                ])
            att = Table(atrows, colWidths=["10%", "30%", "40%", "20%"],
                        style=TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                            ("BACKGROUND", (0, 1), (-1, -1), GRAY6),
                            ("TOPPADDING",    (0, 0), (-1, -1), 3),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
                            ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.white),
                        ]))
            block.append(att)
            block.append(sp(1))

    story = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    cd   = r.get("council_decision") or {}
    rec  = cd.get("final_recommendation", "N/A")
    cons = cd.get("consensus_level", "N/A")

    story.append(sp(8))
    story.append(Paragraph("UNICC AI Safety Council", cover_title))
    story.append(Paragraph("Full Assessment Report", cover_sub))
    story.append(sp(2))

    dec_color = decision_color(rec)
    story.append(Table(
        [[Paragraph(f'<font color="{dec_color.hexval()}"><b>{rec}</b></font>', S("Dec", fontSize=18, fontName="Helvetica-Bold")),
          Paragraph(f"Consensus: {cons}", S("Cons", fontSize=10, textColor=GRAY5))]],
        colWidths=["60%", "40%"],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GRAY6),
            ("ROUNDEDCORNERS", (0, 0), (-1, -1), [4, 4, 4, 4]),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ]),
    ))
    story.append(sp(3))
    story.append(Paragraph(f"<b>System:</b>  {safe(r.get('system_name', r.get('agent_id', '')))}",  cover_meta))
    story.append(Paragraph(f"<b>Agent ID:</b> {safe(r.get('agent_id', ''))}",  cover_meta))
    story.append(Paragraph(f"<b>Incident:</b> {safe(r.get('incident_id', ''))}",  cover_meta))
    story.append(Paragraph(f"<b>Timestamp:</b> {safe(r.get('timestamp', '')[:19].replace('T', ' '))} UTC",  cover_meta))
    story.append(hr())

    story.append(Paragraph("0. System Under Evaluation", h1_style))
    story.append(Paragraph(safe(r.get("system_description") or "", 1200), body_style))
    story.append(hr())

    story.append(Paragraph("1. Expert Analyses &amp; Judgments", h1_style))
    expert_map = {
        "security":      ("🔒", "Expert 1 — Security &amp; Adversarial"),
        "governance":    ("⚖️",  "Expert 2 — Governance &amp; Compliance"),
        "un_mission_fit":("🌐", "Expert 3 — UN Mission Fit"),
    }
    for key, (icon, title) in expert_map.items():
        er = (r.get("expert_reports") or {}).get(key, {})
        if not er:
            continue
        exp_rec = er.get("recommendation", "N/A")
        ec = decision_color(exp_rec)
        block = []
        block.append(Paragraph(
            f'{title} — <font color="{ec.hexval()}"><b>{exp_rec}</b></font>', h2_style))

        if er.get("error"):
            block.append(Paragraph(f"⚠ Module error: {safe(er['error'])}", small_style))
        else:
            dim_scores = er.get("dimension_scores") or {}
            if dim_scores:
                block.append(Paragraph("Dimension Scores", label_style))
                rows = [[Paragraph(f"<b>{k.replace('_',' ').title()}</b>", small_style),
                         Paragraph(str(v), small_style)]
                        for k, v in dim_scores.items()]
                t = Table(rows, colWidths=["60%", "40%"],
                          style=TableStyle([
                              ("BACKGROUND", (0, 0), (-1, -1), GRAY6),
                              ("TOPPADDING",    (0, 0), (-1, -1), 3),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                              ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                          ]))
                block.append(t)
                block.append(sp(2))

            findings = er.get("key_findings") or []
            if findings:
                render_findings(block, findings)

            narrative = er.get("narrative") or ""
            if narrative:
                block.append(Paragraph("Narrative", label_style))
                block.append(Paragraph(safe(narrative, 800), body_style))

            violations = er.get("un_principle_violations") or er.get("key_gaps") or []
            if violations:
                block.append(Paragraph("Compliance Gaps / Violations", label_style))
                for v in violations[:5]:
                    block.append(Paragraph(f"• {safe(v, 300)}", bullet_style))

            atlas = er.get("atlas_citations") or []
            if atlas:
                block.append(Paragraph("ATLAS Citations", label_style))
                for cite in atlas[:8]:
                    if isinstance(cite, dict):
                        cid   = safe(cite.get("id", ""), 30)
                        cname = safe(cite.get("name", ""), 60)
                        rel   = cite.get("relevance", "")
                        rel_str = f"  (rel: {rel:.2f})" if isinstance(rel, (int, float)) else ""
                        block.append(Paragraph(f"§ {cid} — {cname}{rel_str}", bullet_style))
                    else:
                        block.append(Paragraph(f"§ {safe(str(cite), 120)}", bullet_style))

            if key == "security":
                render_attack_trail(block, er)

        story.append(KeepTogether(block))
        story.append(sp(2))

    story.append(hr())

    story.append(Paragraph("2. Council Debate (Cross-Expert Critiques)", h1_style))
    critiques = r.get("critiques") or {}
    for i, (ckey, cv) in enumerate(critiques.items()):
        agrees = cv.get("agrees", True)
        agree_label = "Agrees" if agrees else "Disagrees"
        agree_color = GREEN.hexval() if agrees else ORANGE.hexval()
        from_e = cv.get("from_expert", "").replace("_", " ").title()
        on_e   = cv.get("on_expert",   "").replace("_", " ").title()
        block = []
        block.append(Paragraph(
            f'Critique {i+1}: {safe(from_e)} → {safe(on_e)} '
            f'— <font color="{agree_color}"><b>{agree_label}</b></font>',
            h3_style))
        kp = safe(cv.get("key_point", ""), 400)
        block.append(Paragraph(f'<i>"{kp}"</i>', body_style))
        stance = safe(cv.get("stance", ""), 200)
        if stance:
            block.append(Paragraph(f"<b>Stance:</b> {stance}", small_style))
        for ev in (cv.get("evidence_references") or [])[:3]:
            block.append(Paragraph(f"§ {safe(ev, 200)}", bullet_style))
        story.append(KeepTogether(block))
        story.append(sp(1))

    story.append(hr())

    story.append(Paragraph("3. Expert Final Opinions &amp; Arbitration", h1_style))
    rows = []
    for key, (_, title) in expert_map.items():
        er = (r.get("expert_reports") or {}).get(key, {})
        exp_rec = er.get("recommendation", "N/A")
        ec = decision_color(exp_rec)
        rows.append([
            Paragraph(title, small_style),
            Paragraph(f'<font color="{ec.hexval()}"><b>{exp_rec}</b></font>', small_style),
        ])
    t = Table(rows, colWidths=["70%", "30%"],
              style=TableStyle([
                  ("BACKGROUND", (0, 0), (-1, -1), GRAY6),
                  ("TOPPADDING",    (0, 0), (-1, -1), 4),
                  ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                  ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                  ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.white),
              ]))
    story.append(t)
    story.append(sp(3))

    story.append(Paragraph("Council Decision", h2_style))
    dec_col = decision_color(rec)
    story.append(Table(
        [[Paragraph(f'<font color="{dec_col.hexval()}"><b>{rec}</b></font>',
                    S("BigDec", fontSize=16, fontName="Helvetica-Bold")),
          Paragraph(
              f"Consensus: <b>{cons}</b><br/>"
              f"Human Oversight: <b>{cd.get('human_oversight_required','?')}</b><br/>"
              f"Blocks Deployment: <b>{cd.get('compliance_blocks_deployment','?')}</b>",
              small_style)]],
        colWidths=["35%", "65%"],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GRAY6),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ]),
    ))
    story.append(sp(3))

    rationale = cd.get("rationale") or r.get("council_note") or ""
    if rationale:
        story.append(Paragraph("Rationale", label_style))
        story.append(Paragraph(safe(rationale, 1200), body_style))

    story.append(hr())
    story.append(Paragraph(
        "This report was generated by the UNICC AI Safety Council automated pipeline. "
        "All findings should be reviewed by qualified human evaluators before any deployment decision.",
        S("Footer", fontSize=8, textColor=GRAY5,
          alignment=1)  # TA_CENTER = 1
    ))

    doc.build(story)
    return buf.getvalue()
