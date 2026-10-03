import os
import io
from typing import List, Dict, Optional
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from backend.config import settings

def set_cell_background(cell, fill_hex: str):
    """Sets background color of a docx table cell"""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets padding/margins for table cell in dxa"""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def format_docx(
    title: str,
    content: str,
    summary_table: Optional[List[Dict[str, str]]] = None,
    document_type: Optional[str] = None
) -> io.BytesIO:
    """
    Generates a professional legal DOCX document:
    - 1-inch standard legal margins
    - High-res LegalEase logo
    - Dark Navy & Gold styled headings
    - Executive Terms Summary Table
    - Numbered legal clauses and paragraph spacing
    - Signature blocks
    - Running footer with legal disclaimer
    """
    doc = Document()
    
    # 1. Page Margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Header: Logo & Branding
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("LEGALEASE | AI LEGAL DRAFTING SYSTEM")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(148, 163, 184) # Slate
        
        # Footer: Legal Disclaimer & Page indicator
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run(
            "LegalEase — AI-Assisted Legal Document Generator\n"
            "Confidential & Prepared for Drafting Purposes Only. Not Formal Legal Advice."
        )
        frun.font.name = "Arial"
        frun.font.size = Pt(8)
        frun.font.color.rgb = RGBColor(148, 163, 184)

    # 2. Add Logo if available
    logo_path = settings.LOGO_PATH
    if os.path.exists(logo_path):
        try:
            logo_p = doc.add_paragraph()
            logo_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            logo_p.paragraph_format.space_after = Pt(14)
            logo_run = logo_p.add_run()
            logo_run.add_picture(str(logo_path), width=Inches(3.8))
        except Exception:
            pass

    # 3. Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(6)
    
    run_title = p_title.add_run(title.upper())
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(10, 17, 40) # Dark Navy #0A1128
    
    if document_type and document_type.upper() != title.upper():
        p_sub = doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub.paragraph_format.space_after = Pt(14)
        run_sub = p_sub.add_run(f"Type: {document_type}")
        run_sub.font.name = "Times New Roman"
        run_sub.font.size = Pt(11)
        run_sub.font.italic = True
        run_sub.font.color.rgb = RGBColor(212, 175, 55) # Gold #D4AF37

    # 4. Key Terms Summary Table (if provided)
    if summary_table and len(summary_table) > 0:
        p_tbl_heading = doc.add_paragraph()
        p_tbl_heading.paragraph_format.space_before = Pt(12)
        p_tbl_heading.paragraph_format.space_after = Pt(4)
        r_th = p_tbl_heading.add_run("EXECUTIVE SUMMARY OF KEY TERMS")
        r_th.font.name = "Times New Roman"
        r_th.font.size = Pt(12)
        r_th.font.bold = True
        r_th.font.color.rgb = RGBColor(10, 17, 40)
        
        table = doc.add_table(rows=len(summary_table) + 1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        
        # Set column widths
        for row in table.rows:
            row.cells[0].width = Inches(2.2)
            row.cells[1].width = Inches(4.3)
            
        # Header Row
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "CONTRACT TERM"
        hdr_cells[1].text = "AGREED DETAILS"
        for i in [0, 1]:
            set_cell_background(hdr_cells[i], "0A1128") # Navy
            set_cell_margins(hdr_cells[i], top=120, bottom=120, left=150, right=150)
            p = hdr_cells[i].paragraphs[0]
            for run in p.runs:
                run.font.name = "Arial"
                run.font.size = Pt(9.5)
                run.font.bold = True
                run.font.color.rgb = RGBColor(212, 175, 55) # Gold
                
        # Data Rows
        for idx, item in enumerate(summary_table):
            row_cells = table.rows[idx + 1].cells
            row_cells[0].text = str(item.get("term", ""))
            row_cells[1].text = str(item.get("details", ""))
            bg_color = "F8FAFC" if idx % 2 == 0 else "FFFFFF"
            for i in [0, 1]:
                set_cell_background(row_cells[i], bg_color)
                set_cell_margins(row_cells[i], top=80, bottom=80, left=150, right=150)
                p = row_cells[i].paragraphs[0]
                for run in p.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(10)
                    if i == 0:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(15, 23, 42)
                    else:
                        run.font.color.rgb = RGBColor(30, 41, 59)
                        
        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_before = Pt(12)

    # 5. Document Content / Legal Clauses
    # Parse lines from content, detecting headers, list items, and standard body text
    content_lines = content.split("\n")
    for raw_line in content_lines:
        line = raw_line.strip()
        if not line:
            continue
            
        # Skip decorative separators like "=====" or "------"
        if set(line) in [{'-'}, {'='}, {'*'}]:
            continue
            
        # Skip redundant raw title repetitions if already printed at top
        if line.upper() == title.upper():
            continue
            
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        
        # Check if line is a major Section Heading (e.g. "1. SCOPE", "RECITALS", "IN WITNESS WHEREOF")
        is_heading = (
            (line.isupper() and len(line) < 60) or
            any(line.startswith(prefix) for prefix in ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]) and len(line) < 65
        )
        
        if is_heading:
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(line)
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = RGBColor(10, 17, 40) # Navy
        elif line.startswith("•") or line.startswith("- "):
            p.paragraph_format.left_indent = Inches(0.25)
            clean_bullet = line.lstrip("•- ")
            run = p.add_run("•  " + clean_bullet)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(15, 23, 42)
        elif line.startswith("DISCLAIMER:") or line.startswith("LEGAL DISCLAIMER:"):
            p.paragraph_format.space_before = Pt(16)
            run = p.add_run(line)
            run.font.name = "Times New Roman"
            run.font.size = Pt(9.5)
            run.font.italic = True
            run.font.color.rgb = RGBColor(100, 116, 139)
        else:
            run = p.add_run(line)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(15, 23, 42)
            
    # Save to memory buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
