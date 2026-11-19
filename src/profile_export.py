"""PDF exports for learner-owned EduBridge AI profile data."""
from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, KeepTogether,
)


def build_profile_pdf(profile: dict) -> bytes:
    """Create a readable PDF summary from a learner's own saved profile."""
    if not isinstance(profile, dict) or not profile:
        raise ValueError("A non-empty learning profile is required.")

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title="EduBridge AI — Learning Profile",
        author="EduBridge AI",
    )
    base = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "EduTitle", parent=base["Title"], fontName="Helvetica-Bold",
        fontSize=23, leading=27, textColor=colors.HexColor("#252653"),
        alignment=TA_LEFT, spaceAfter=5,
    )
    subtitle_style = ParagraphStyle(
        "EduSubtitle", parent=base["Normal"], fontSize=9,
        textColor=colors.HexColor("#68708D"), leading=14, spaceAfter=14,
    )
    section_style = ParagraphStyle(
        "EduSection", parent=base["Heading2"], fontName="Helvetica-Bold",
        fontSize=12, leading=16, textColor=colors.HexColor("#5B50D6"),
        spaceBefore=12, spaceAfter=7,
    )
    body_style = ParagraphStyle(
        "EduBody", parent=base["BodyText"], fontSize=9,
        leading=13, textColor=colors.HexColor("#343852"),
    )
    small_style = ParagraphStyle(
        "EduSmall", parent=base["BodyText"], fontSize=8,
        leading=11, textColor=colors.HexColor("#737A95"),
    )

    def safe(value):
        return escape(str(value if value not in (None, "") else "Not provided"))

    story = [
        Paragraph("EduBridge AI", title_style),
        Paragraph("LEARNING PROFILE · PERSONAL EXPORT", subtitle_style),
        Paragraph(
            "A snapshot of the learning information you chose to save. "
            "Self-reported confidence is for reflection and planning, not grading or prediction.",
            body_style,
        ),
        Spacer(1, 8),
    ]

    overview_rows = [
        ["Education level", safe(profile.get("level"))],
        ["Curriculum / programme", safe(profile.get("board"))],
        ["Field of interest", safe(profile.get("pathway"))],
        ["Programme / group", safe(profile.get("programme"))],
        ["Current class / year", safe(profile.get("current_year"))],
        ["Weekly study budget", f"{safe(profile.get('weekly_hours'))} hour(s)"],
        ["Last updated", safe(profile.get("updated"))],
    ]
    story.append(Paragraph("Your learning overview", section_style))
    overview = Table(overview_rows, colWidths=[48 * mm, 118 * mm], hAlign="LEFT")
    overview.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0EFFF")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#4F49A8")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEADING", (0, 0), (-1, -1), 12),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E4E6F2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(overview)

    subjects = profile.get("subjects") or []
    confidence = profile.get("confidence") or {}
    latest = profile.get("latest_results") or {}
    story.append(Paragraph("Subjects & self-reflection", section_style))
    subject_rows = [["Subject", "Confidence (1–5)", "Latest result (optional)"]]
    for subject in subjects:
        subject_rows.append([
            safe(subject),
            safe(confidence.get(subject, "Not rated")),
            safe(latest.get(subject, "Not entered")),
        ])
    if len(subject_rows) == 1:
        subject_rows.append(["No subjects added", "—", "—"])
    subject_table = Table(subject_rows, colWidths=[65 * mm, 43 * mm, 58 * mm], repeatRows=1)
    subject_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#252653")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E4E6F2")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F8FD")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(subject_table)

    institution = profile.get("institution")
    if institution:
        story.append(Paragraph("Institution", section_style))
        story.append(Paragraph(safe(institution), body_style))

    story.extend([
        Spacer(1, 14),
        Paragraph(
            "<b>Privacy note:</b> This PDF contains information you entered into your profile. "
            "Store and share it carefully. EduBridge AI does not infer grades, admissions chances, "
            "diagnoses or future academic outcomes from this profile.",
            small_style,
        ),
        Spacer(1, 6),
        Paragraph("EduBridge AI · Learn · Explore · Grow", small_style),
    ])

    document.build(story)
    return buffer.getvalue()
