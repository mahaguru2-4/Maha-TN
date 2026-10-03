import html
import re

def sanitize_text(text: str) -> str:
    """
    Sanitize text input safely:
    - Normalizes unicode quotes, hyphens, and whitespace
    - Strips hazardous control characters while preserving legal newlines and tabs
    - Preserves legal formatting and terms
    """
    if not text:
        return ""
    
    # Replace non-standard dashes and smart quotes with clean ASCII equivalents
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "--",
        "\u2026": "...",
        "\u00a0": " ",  # non-breaking space
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
        
    # Remove null bytes and hazardous control characters (keep \n, \r, \t)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalize Windows vs Unix line endings to \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Limit consecutive blank lines to at most 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def sanitize_html(text: str) -> str:
    """
    Escapes HTML entities to prevent XSS in rendered previews.
    """
    if not text:
        return ""
    return html.escape(text)

def clean_filename(name: str) -> str:
    """
    Creates safe filename from document title.
    """
    if not name:
        return "document"
    # Replace non-alphanumeric with underscores
    clean = re.sub(r'[^a-zA-Z0-9_\- ]', '', name)
    clean = clean.strip().replace(" ", "_")
    return clean[:60] or "legal_document"
