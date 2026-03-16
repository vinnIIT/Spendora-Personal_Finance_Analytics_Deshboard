from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
import datetime

def generate_pdf(name, selected_month, df):

    file_path = "analysis_report.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    download_time = datetime.datetime.now().strftime("%d %B %Y | %I:%M %p")

    elements.append(Paragraph(f"<b>NAME:</b> {name}", styles["Normal"]))
    elements.append(Paragraph(f"<b> Month:</b> {selected_month}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Downloaded On:</b> {download_time}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("<b>Financial Statement</b>", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    data = [df.columns.tolist()] + df.values.tolist()

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))

    elements.append(table)

    doc.build(elements)

    return file_path