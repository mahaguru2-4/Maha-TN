import os
import io
from typing import List, Dict, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
    HRFlowable
)
from reportlab.pdfgen import canvas
from backend.config import settings

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and display total page count:
    'LegalEase — AI-Assisted Legal Document Generator | Page X of Y'
    """
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
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Header banner rule
        self.setStrokeColor(colors.HexColor("#0A1128"))
        self.setLineWidth(0.5)
        self.line(54, letter[1] - 40, letter[0] - 54, letter[1] - 40)
        
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#D4AF37"))
        self.drawString(54, letter[1] - 35, "LEGALEASE")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawRightString(letter[0] - 54, letter[1] - 35, "AI-ASSISTED LEGAL DRAFT")
        
        # Footer rule
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(54, 45, letter[0] - 54, 45)
        
        # Footer text
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(54, 32, "LegalEase — AI-Assisted Legal Document Generator | Informational Draft")
        
        # Page count
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_text)
        
        self.restoreState()

def format_pdf(
    title: str,
    content: str,
    summary_table: Optional[List[Dict[str, str]]] = None,
    document_type: Optional[str] = None
) -> io.BytesIO:
    """
    Builds a legal-grade PDF with ReportLab:
    - 0.75 in margins
    - High-res LegalEase logo
    - Deep Navy & Gold visual identity
    - Structured Terms Table with alternating rows
    - Numbered legal clauses
    - Signatures block
    - Running headers, footers & page numbers
    """
    buffer = io.BytesIO()
    
    # 0.75 in = 54 pt margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Brand Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0A1128"),
        alignment=1, # Center
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#D4AF37"),
        alignment=1,
        spaceAfter=14
    )
    
    table_hdr_style = ParagraphStyle(
        "TableHdr",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0A1128"),
        spaceBefore=10,
        spaceAfter=6
    )
    
    cell_term_style = ParagraphStyle(
        "CellTerm",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0F172A")
    )
    
    cell_val_style = ParagraphStyle(
        "CellVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    
    clause_heading_style = ParagraphStyle(
        "ClauseHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0A1128"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        "LegalBody",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        "LegalBullet",
        parent=body_style,
        leftIndent=15,
        spaceAfter=4
    )
    
    disclaimer_style = ParagraphStyle(
        "LegalDisclaimer",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#64748B"),
        spaceBefore=12,
        spaceAfter=8
    )

    story = []
    
    # 1. Logo
    logo_path = settings.LOGO_PATH
    if os.path.exists(logo_path):
        try:
            # 3.2 inch width logo
            story.append(Image(str(logo_path), width=3.2 * inch, height=0.8 * inch))
            story.append(Spacer(1, 10))
        except Exception:
            pass

    # 2. Title & Subtitle
    story.append(Paragraph(title.upper(), title_style))
    if document_type:
        story.append(Paragraph(f"Category: {document_type}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#D4AF37"), spaceAfter=12))

    # 3. Executive Terms Summary Table
    if summary_table and len(summary_table) > 0:
        story.append(Paragraph("EXECUTIVE SUMMARY OF KEY TERMS", table_hdr_style))
        
        table_data = [[
            Paragraph("<b>CONTRACT TERM</b>", ParagraphStyle('H1', parent=cell_term_style, textColor=colors.HexColor("#D4AF37"))),
            Paragraph("<b>AGREED DETAILS</b>", ParagraphStyle('H2', parent=cell_val_style, textColor=colors.HexColor("#FFFFFF"), fontName="Helvetica-Bold"))
        ]]
        
        for item in summary_table:
            t = Paragraph(str(item.get("term", "")), cell_term_style)
            d = Paragraph(str(item.get("details", "")), cell_val_style)
            table_data.append([t, d])
            
        t_flowable = Table(table_data, colWidths=[2.2 * inch, 4.8 * inch])
        t_flowable.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0A1128")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#FFFFFF")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.HexColor("#FFFFFF")]),
        ]))
        
        story.append(t_flowable)
        story.append(Spacer(1, 14))

    # 4. Clauses & Document Body
    raw_lines = content.split("\n")
    for raw in raw_lines:
        line = raw.strip()
        if not line:
            continue
            
        # Ignore horizontal line dividers
        if set(line) in [{'-'}, {'='}, {'*'}]:
            continue
            
        # If line is identical to main title already output, skip
        if line.upper() == title.upper():
            continue
            
        is_heading = (
            (line.isupper() and len(line) < 60) or
            any(line.startswith(p) for p in ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]) and len(line) < 65
        )
        
        if is_heading:
            story.append(Paragraph(line, clause_heading_style))
        elif line.startswith("•") or line.startswith("- "):
            clean = line.lstrip("•- ")
            story.append(Paragraph(f"• &nbsp; {clean}", bullet_style))
        elif line.startswith("DISCLAIMER:") or line.startswith("LEGAL DISCLAIMER:"):
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"<b>{line}</b>", disclaimer_style))
        else:
            story.append(Paragraph(line, body_style))

    # Build PDF using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
