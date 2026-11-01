"""Build WAHA vs Evolution comparison as DOCX and PDF."""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

POC_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = POC_ROOT / "docs" / "screenshots"
OUT_DOCX = POC_ROOT / "WAHA-vs-Evolution-Comparison.docx"
OUT_PDF = POC_ROOT / "WAHA-vs-Evolution-Comparison.pdf"


def set_cell_shading(cell, fill: str) -> None:
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(shading)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], header_fill: str = "25D366") -> None:
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, text in enumerate(headers):
        hdr[i].text = text
        set_cell_shading(hdr[i], header_fill)
        for p in hdr[i].paragraphs:
            for run in p.runs:
                run.bold = True
                run.font.color.rgb = None
    for r_idx, row in enumerate(rows):
        cells = table.rows[r_idx + 1].cells
        for c_idx, text in enumerate(row):
            cells[c_idx].text = text
    doc.add_paragraph()


def add_image(doc: Document, name: str, caption: str, width_in: float = 5.8) -> None:
    path = SCREENSHOTS / name
    if path.is_file():
        doc.add_paragraph(caption, style="Intense Quote")
        doc.add_picture(str(path), width=Inches(width_in))
        doc.add_paragraph()
    else:
        doc.add_paragraph(f"[Missing image: {name}] {caption}")


def build_docx() -> Path:
    doc = Document()
    title = doc.add_heading("WAHA vs Evolution API", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_paragraph("Comparison & recommendation (WhatsApp POC)")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].italic = True
    doc.add_paragraph()

    doc.add_heading("Overview", level=1)
    doc.add_paragraph(
        "Both POCs share the same Flask product flow: login → QR connect → sync contacts → "
        "compose/campaign. Only the WhatsApp engine behind the API differs."
    )

    doc.add_heading("Shared Flask flow", level=2)
    add_table(
        doc,
        ["Step", "Flow"],
        [
            ["1", "Login admin / admin123"],
            ["2", "Connect — start session/instance, scan QR"],
            ["3", "Contacts — sync from WhatsApp"],
            ["4", "Compose — free-text message"],
            ["5", "Campaign — queue send to selected contacts"],
        ],
    )

    doc.add_heading("POC folders & ports", level=2)
    add_table(
        doc,
        ["Folder", "Engine", "Flask app", "Engine port"],
        [
            ["poc/waha-poc/", "WAHA", "http://127.0.0.1:5001", "3000"],
            ["poc/evolution-poc/", "Evolution API", "http://127.0.0.1:5002", "8080"],
        ],
        header_fill="128C7E",
    )

    doc.add_heading("Admin UIs (screenshots)", level=1)

    doc.add_heading("WAHA — built-in dashboard", level=2)
    doc.add_paragraph("URL: http://127.0.0.1:3000/dashboard/")
    doc.add_paragraph(
        "Auth: Username + password from waha-env/.env; link worker with WAHA_API_KEY."
    )
    add_image(doc, "waha-dashboard-workers.png", "WAHA dashboard — workers and sessions")

    doc.add_heading("Evolution — Evolution Manager", level=2)
    doc.add_paragraph("URL: http://127.0.0.1:8080/manager")
    doc.add_paragraph("Auth: Global API key only (same as EVOLUTION_API_KEY).")
    add_image(doc, "evolution-manager-login.png", "Evolution Manager login")
    add_image(doc, "evolution-manager-instances.png", "Evolution Manager — instances")

    doc.add_heading("Flask demo (both POCs)", level=2)
    doc.add_paragraph(
        "Same UX on ports 5001 (WAHA) and 5002 (Evolution): Connect, Contacts, Compose, Campaigns. "
        "Use for stakeholder demos; use native UIs for engine debugging."
    )

    doc.add_heading("Side-by-side comparison", level=1)
    add_table(
        doc,
        ["Criteria", "WAHA", "Evolution API"],
        [
            ["Docker footprint", "1 container (WAHA only)", "3 containers (API + Postgres + Redis)"],
            ["First-time setup", "init-waha.bat + sync API key to Flask .env", "Matching API key in compose + .env; longer first pull"],
            ["Admin login", "Username + password + API key for worker", "API key only on Manager"],
            ["Session model", "Named sessions (default)", "Named instances (default)"],
            ["QR connect", "Works; 422 if QR while STARTING", "Works; create/start instance first"],
            ["Contact sync", "Straightforward API in our client", "v2 POST findContacts with {\"where\":{}}"],
            ["API auth header", "X-Api-Key", "apikey"],
            ["Multi-instance / SaaS", "Sessions + namespace", "Strong fit — DB, Manager, Redis"],
            ["Best for one number bulk", "Excellent", "Good"],
            ["Best for many numbers", "Good", "Better"],
        ],
    )

    doc.add_heading("POC scorecard", level=1)
    add_table(
        doc,
        ["Criteria", "WAHA", "Evolution"],
        [
            ["Install time", "~5 min (after Docker)", "~10–15 min (DB + Redis + image)"],
            ["QR connected", "Yes", "Yes"],
            ["Contact sync", "Yes", "Yes (after POST fix)"],
            ["Single send", "Yes", "Yes"],
            ["Campaign queue", "Yes", "Yes"],
            ["Stability (short demo)", "Stable", "Stable"],
            ["Docs / ease for devs", "Easier (fewer services)", "More moving parts"],
            ["Native admin UX", "Workers/sessions dashboard", "Polished Manager"],
            ["Pick for this product", "Recommended", "Strong alternate"],
        ],
    )

    doc.add_heading("Legal & operations (both)", level=1)
    for bullet in [
        "Uses WhatsApp Web / Baileys-class linking — not the official Meta Cloud API.",
        "Free-text is possible but policy and ban risk still apply.",
        "Use a dedicated test number, rate limits, and opt-in/consent for marketing.",
        "For compliance-first production, evaluate legacy-cloud-api/ (Cloud API) separately.",
    ]:
        doc.add_paragraph(bullet, style="List Bullet")

    doc.add_heading("Recommendation: what should we use?", level=1)
    doc.add_heading("Primary choice: WAHA", level=2)
    doc.add_paragraph(
        "For one web app, one WhatsApp number, QR login, contact sync, and bulk/campaign sends, "
        "WAHA is the better default engine:"
    )
    for bullet in [
        "Simpler operations — one Docker service, no Postgres/Redis on a laptop or small VPS.",
        "Faster onboarding — init-waha.bat + one API key; clear 401 when keys mismatch.",
        "Enough admin UI — dashboard + Swagger for support staff.",
        "Lower POC friction after credentials were fixed.",
    ]:
        doc.add_paragraph(bullet, style="List Number")

    doc.add_heading("When to choose Evolution instead", level=2)
    for bullet in [
        "Many WhatsApp instances (multi-tenant) with Manager as ops console.",
        "Team already on Evolution webhooks or evoapicloud in production.",
        "Need Evolution ecosystem (chatbots, n8n, etc.) without rebuilding on WAHA.",
    ]:
        doc.add_paragraph(bullet, style="List Bullet")

    doc.add_heading("Decision summary", level=1)
    add_table(
        doc,
        ["Question", "Answer"],
        [
            ["Which engine for v1 product?", "WAHA"],
            ["Which Flask POC to demo first?", "http://127.0.0.1:5001"],
            ["Keep Evolution POC?", "Yes — reference & multi-instance evaluation"],
            ["Official Meta path?", "Separate decision; see legacy-cloud-api/"],
        ],
        header_fill="075E54",
    )

    doc.add_heading("Next steps (optional)", level=1)
    for bullet in [
        "Merge one Flask app + configurable engine (WAHA / EVOLUTION / MOCK).",
        "Improve Connect page: poll until QR-ready (fix WAHA 422 UX).",
        "Stakeholder sign-off using this doc + live demo on 5001.",
        "Production hardening: rotate API keys, HTTPS reverse proxy, secrets not in git.",
    ]:
        doc.add_paragraph(bullet, style="List Number")

    doc.add_paragraph()
    foot = doc.add_paragraph("Generated from poc/COMPARISON.md — WhatsApp POC repository.")
    foot.runs[0].font.size = Pt(9)
    foot.runs[0].italic = True

    doc.save(OUT_DOCX)
    return OUT_DOCX


def build_pdf(docx_path: Path) -> Path | None:
    try:
        from docx2pdf import convert

        convert(str(docx_path), str(OUT_PDF))
        return OUT_PDF if OUT_PDF.is_file() else None
    except Exception as exc:
        print(f"docx2pdf failed ({exc}); trying fallback PDF...", file=sys.stderr)
    return build_pdf_fallback()


def build_pdf_fallback() -> Path | None:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            Image,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError:
        print("Install reportlab for PDF fallback: pip install reportlab", file=sys.stderr)
        return None

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
        alignment=1,
    )
    story = []
    story.append(Paragraph("WAHA vs Evolution API — Comparison &amp; Recommendation", title_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "<b>Recommendation:</b> Use <b>WAHA</b> as the primary engine for v1 "
            "(one number, QR connect, contacts, campaigns). Keep Evolution for multi-instance evaluation.",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.15 * inch))

    data = [
        ["Question", "Answer"],
        ["Engine for v1?", "WAHA"],
        ["Demo URL", "http://127.0.0.1:5001"],
        ["Evolution role", "Reference / multi-instance"],
    ]
    t = Table(data, colWidths=[2.8 * inch, 3.2 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#25D366")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("See WAHA-vs-Evolution-Comparison.docx for full tables and screenshots.", styles["Italic"]))

    for fname, cap in [
        ("waha-dashboard-workers.png", "WAHA dashboard"),
        ("evolution-manager-login.png", "Evolution Manager login"),
        ("evolution-manager-instances.png", "Evolution instances"),
    ]:
        p = SCREENSHOTS / fname
        if p.is_file():
            story.append(Spacer(1, 0.15 * inch))
            story.append(Paragraph(cap, styles["Heading3"]))
            img = Image(str(p), width=5.5 * inch, height=3 * inch, kind="proportional")
            story.append(img)

    SimpleDocTemplate(str(OUT_PDF), pagesize=A4).build(story)
    return OUT_PDF if OUT_PDF.is_file() else None


def main() -> int:
    docx = build_docx()
    print(f"Wrote {docx}")
    pdf = build_pdf(docx)
    if pdf:
        print(f"Wrote {pdf}")
    else:
        print("PDF not created — open DOCX in Word and Save as PDF.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
