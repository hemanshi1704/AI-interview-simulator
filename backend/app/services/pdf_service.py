import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.config import get_settings

settings = get_settings()


def generate_report(session, questions, candidate_name: str, target_role: str) -> str:
    os.makedirs(settings.report_dir, exist_ok=True)
    file_path = os.path.join(settings.report_dir, f"report_{session.id}.pdf")

    doc = SimpleDocTemplate(file_path, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleX", parent=styles["Title"], fontSize=20)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=14)
    body = styles["BodyText"]

    story = []
    story.append(Paragraph("AI Interview Feedback Report", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Candidate: {candidate_name}", body))
    story.append(Paragraph(f"Target role: {target_role}", body))
    story.append(Spacer(1, 12))

    summary_data = [
        ["Overall Technical Score", f"{session.overall_technical_score:.1f} / 10"],
        ["Overall Communication Score", f"{session.overall_communication_score:.1f} / 10"],
    ]
    table = Table(summary_data, colWidths=[9 * cm, 5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Question-by-Question Breakdown", h2))
    for q in questions:
        story.append(Paragraph(f"Q{q.order_index + 1} ({q.category}): {q.question_text}", styles["Heading4"]))
        story.append(Paragraph(f"<i>Answer:</i> {q.answer_text or '—'}", body))
        story.append(Paragraph(
            f"Technical: {q.technical_score or 0:.1f}/10 &nbsp;&nbsp; "
            f"Communication: {q.communication_score or 0:.1f}/10", body))
        story.append(Paragraph(f"<i>Feedback:</i> {q.feedback or '—'}", body))
        story.append(Spacer(1, 10))

    doc.build(story)
    return file_path
