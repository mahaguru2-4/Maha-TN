import html
from typing import List, Dict, Optional

def format_html_preview(
    title: str,
    content: str,
    summary_table: Optional[List[Dict[str, str]]] = None,
    document_type: Optional[str] = None
) -> str:
    """
    Renders the legal document in clean, high-contrast, responsive HTML
    suitable for inline Streamlit preview with Dark Navy & Gold highlights.
    """
    safe_title = html.escape(title)
    safe_doc_type = html.escape(document_type or "")
    
    html_parts = []
    
    html_parts.append("""
    <div style="
        font-family: 'Times New Roman', Georgia, serif;
        background-color: #0d1527;
        color: #f1f5f9;
        padding: 36px 40px;
        border-radius: 12px;
        border: 1px solid #2a3756;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        max-width: 860px;
        margin: 0 auto;
        line-height: 1.7;
    ">
    """)
    
    # Header Emblem & Title
    html_parts.append(f"""
        <div style="text-align: center; border-bottom: 2px solid #d4af37; padding-bottom: 20px; margin-bottom: 24px;">
            <div style="font-family: 'Arial', sans-serif; font-size: 13px; letter-spacing: 3px; color: #d4af37; font-weight: bold; margin-bottom: 6px;">
                ⚖️ LEGALEASE AI DRAFTING SYSTEM
            </div>
            <h1 style="font-size: 24px; color: #ffffff; margin: 0; text-transform: uppercase; letter-spacing: 1px;">
                {safe_title}
            </h1>
    """)
    if safe_doc_type:
        html_parts.append(f"""
            <div style="font-size: 13px; color: #94a3b8; font-style: italic; margin-top: 6px;">
                Category: {safe_doc_type}
            </div>
        """)
    html_parts.append("</div>")
    
    # Executive Summary Table
    if summary_table and len(summary_table) > 0:
        html_parts.append("""
        <div style="margin-bottom: 28px;">
            <div style="font-family: 'Arial', sans-serif; font-size: 13px; font-weight: bold; color: #d4af37; margin-bottom: 8px; letter-spacing: 1px;">
                EXECUTIVE SUMMARY OF KEY TERMS
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px; border: 1px solid #2a3756; background-color: #121c35;">
                <thead>
                    <tr style="background-color: #070d1d; border-bottom: 2px solid #d4af37;">
                        <th style="padding: 10px 14px; text-align: left; color: #d4af37; font-family: 'Arial', sans-serif; font-size: 12px; width: 30%;">TERM</th>
                        <th style="padding: 10px 14px; text-align: left; color: #ffffff; font-family: 'Arial', sans-serif; font-size: 12px;">AGREED DETAILS</th>
                    </tr>
                </thead>
                <tbody>
        """)
        for idx, row in enumerate(summary_table):
            term = html.escape(str(row.get("term", "")))
            details = html.escape(str(row.get("details", "")))
            bg = "#121c35" if idx % 2 == 0 else "#162242"
            html_parts.append(f"""
                <tr style="background-color: {bg}; border-bottom: 1px solid #1e293b;">
                    <td style="padding: 9px 14px; font-weight: bold; color: #cbd5e1;">{term}</td>
                    <td style="padding: 9px 14px; color: #e2e8f0;">{details}</td>
                </tr>
            """)
        html_parts.append("""
                </tbody>
            </table>
        </div>
        """)
        
    # Document Body / Clauses
    raw_lines = content.split("\n")
    for raw in raw_lines:
        line = raw.strip()
        if not line:
            continue
            
        if set(line) in [{'-'}, {'='}, {'*'}]:
            continue
            
        if line.upper() == title.upper():
            continue
            
        safe_line = html.escape(line)
        
        is_heading = (
            (line.isupper() and len(line) < 60) or
            any(line.startswith(p) for p in ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]) and len(line) < 65
        )
        
        if is_heading:
            html_parts.append(f"""
                <h3 style="
                    font-family: 'Arial', sans-serif;
                    font-size: 15px;
                    color: #d4af37;
                    border-left: 3px solid #d4af37;
                    padding-left: 10px;
                    margin-top: 20px;
                    margin-bottom: 8px;
                    text-transform: uppercase;
                ">{safe_line}</h3>
            """)
        elif line.startswith("•") or line.startswith("- "):
            clean = html.escape(line.lstrip("•- "))
            html_parts.append(f"""
                <div style="margin-left: 20px; margin-bottom: 6px; color: #e2e8f0; font-size: 15px;">
                    <span style="color: #d4af37; margin-right: 6px;">▪</span> {clean}
                </div>
            """)
        elif line.startswith("DISCLAIMER:") or line.startswith("LEGAL DISCLAIMER:"):
            html_parts.append(f"""
                <div style="
                    margin-top: 30px;
                    padding: 14px 18px;
                    background-color: #080f21;
                    border-left: 4px solid #f59e0b;
                    border-radius: 6px;
                    font-size: 13px;
                    color: #94a3b8;
                    font-style: italic;
                    line-height: 1.5;
                ">
                    <strong style="color: #f59e0b;">LEGAL DISCLAIMER:</strong> {safe_line.replace('DISCLAIMER:', '').replace('LEGAL DISCLAIMER:', '')}
                </div>
            """)
        elif "________________" in line:
            # Signature line
            html_parts.append(f"""
                <div style="color: #cbd5e1; font-family: monospace; font-size: 14px; margin: 4px 0;">
                    {safe_line}
                </div>
            """)
        else:
            html_parts.append(f"""
                <p style="margin-bottom: 12px; font-size: 15px; color: #e2e8f0; text-align: justify;">
                    {safe_line}
                </p>
            """)
            
    html_parts.append("</div>")
    return "\n".join(html_parts)
