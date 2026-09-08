"""
Professional resume DOCX generator using python-docx.
Produces a clean, ATS-compatible, visually polished Word document.
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re

# ── Color palette ─────────────────────────────────────────────────────────────
ACCENT_COLOR   = RGBColor(31, 78, 121)   # navy blue
DARK_COLOR     = RGBColor(30, 30, 30)    # near-black body
MID_COLOR      = RGBColor(90, 90, 90)    # gray for dates/sub-info

DATE_RE = re.compile(
    r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}'
    r'\s*[–\-—]\s*'
    r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec[a-z]*\.?\s+\d{4}|Present|Current|Now|\d{4}))',
    re.IGNORECASE
)


def _clean(text):
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'\*{1,3}', '', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\-\*]\s+', '• ', text, flags=re.MULTILINE)
    return text.strip()


def _set_paragraph_spacing(para, before=0, after=0, line_rule=None, line_val=None):
    pPr = para._p.get_or_add_pPr()
    pPPr = OxmlElement('w:spacing')
    pPPr.set(qn('w:before'), str(before))
    pPPr.set(qn('w:after'),  str(after))
    if line_rule and line_val:
        pPPr.set(qn('w:lineRule'), line_rule)
        pPPr.set(qn('w:line'),     str(line_val))
    pPr.append(pPPr)


def _add_horizontal_rule(doc):
    """Add a thin horizontal rule paragraph."""
    p = doc.add_paragraph()
    _set_paragraph_spacing(p, before=20, after=20)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'),   'single')
    bottom.set(qn('w:sz'),    '4')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'B4C6E7')
    pBdr.append(bottom)
    pPr.append(pBdr)


def _add_name(doc, name_text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(p, before=0, after=40)
    run = p.add_run(name_text)
    run.bold = True
    run.font.size = Pt(22)
    run.font.color.rgb = ACCENT_COLOR


def _add_contact(doc, contact_text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_spacing(p, before=0, after=60)
    run = p.add_run(contact_text)
    run.font.size = Pt(9)
    run.font.color.rgb = MID_COLOR


def _add_section_header(doc, header_text):
    p = doc.add_paragraph()
    _set_paragraph_spacing(p, before=120, after=20)
    run = p.add_run(header_text.upper())
    run.bold = True
    run.font.size = Pt(10)
    run.font.color.rgb = ACCENT_COLOR
    # Bottom border under section header
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'),   'single')
    bottom.set(qn('w:sz'),    '4')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '1F4E79')
    pBdr.append(bottom)
    pPr.append(pBdr)


def _add_two_col_line(doc, left_text, right_text, left_bold=True):
    """Left-aligned bold title, right-aligned gray date — using a table row."""
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = 'Table Grid'
    # Remove all borders
    for cell in tbl.rows[0].cells:
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
            el = OxmlElement(f'w:{side}')
            el.set(qn('w:val'), 'none')
            tcBorders.append(el)
        tcPr.append(tcBorders)

    left_cell  = tbl.rows[0].cells[0]
    right_cell = tbl.rows[0].cells[1]

    # Set column widths (approx 70% / 30%)
    left_cell.width  = Inches(4.5)
    right_cell.width = Inches(1.9)

    lp = left_cell.paragraphs[0]
    _set_paragraph_spacing(lp, before=20, after=20)
    lr = lp.add_run(left_text)
    lr.bold = left_bold
    lr.font.size = Pt(10)
    lr.font.color.rgb = DARK_COLOR

    rp = right_cell.paragraphs[0]
    rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _set_paragraph_spacing(rp, before=20, after=20)
    rr = rp.add_run(right_text)
    rr.font.size = Pt(9)
    rr.font.color.rgb = MID_COLOR


def _add_bullet(doc, bullet_text):
    clean = re.sub(r'^[•\-\*]\s*', '', bullet_text).strip()
    if not clean:
        return
    p = doc.add_paragraph(style='List Bullet')
    _set_paragraph_spacing(p, before=20, after=20)
    p.paragraph_format.left_indent  = Cm(0.5)
    p.paragraph_format.first_line_indent = Cm(-0.3)
    run = p.add_run(clean)
    run.font.size = Pt(10)
    run.font.color.rgb = DARK_COLOR


def _add_body(doc, text_str):
    p = doc.add_paragraph()
    _set_paragraph_spacing(p, before=20, after=20)
    run = p.add_run(text_str)
    run.font.size = Pt(10)
    run.font.color.rgb = DARK_COLOR


def generate_docx(optimized_text, output_path):
    text  = _clean(optimized_text)
    lines = [l.rstrip() for l in text.split('\n')]

    doc = Document()

    # ── Page margins ──────────────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin    = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin   = Cm(1.8)
        section.right_margin  = Cm(1.8)

    # ── Default font ──────────────────────────────────────────────────────────
    style = doc.styles['Normal']
    font  = style.font
    font.name = 'Calibri'
    font.size = Pt(10)

    # ── State ─────────────────────────────────────────────────────────────────
    name_done    = False
    contact_done = False

    for raw in lines:
        s = raw.strip()

        if not s:
            continue

        # Divider ---
        if re.fullmatch(r'-{2,}', s):
            if not contact_done:
                contact_done = True
            _add_horizontal_rule(doc)
            continue

        # Name (first non-blank line)
        if not name_done:
            name_done = True
            _add_name(doc, s)
            continue

        # Contact (before first ---)
        if not contact_done:
            _add_contact(doc, s)
            continue

        # Section header: ALL CAPS short line without year digits
        if (s.isupper() and 2 <= len(s) <= 50
                and any(c.isalpha() for c in s)
                and not re.search(r'\d{4}', s)):
            _add_section_header(doc, s)
            continue

        # Bullet point
        if s.startswith(('•', '-', '*')) and len(s) > 2:
            _add_bullet(doc, s)
            continue

        # Two-column date line
        dm = DATE_RE.search(s)
        if dm:
            date_str = dm.group(1).strip()
            left_str = s[:dm.start()].strip().rstrip('|–-').strip()
            _add_two_col_line(doc, left_str, date_str, left_bold=True)
            continue

        # Pipe-separated (Company | Role) without date
        if '|' in s and len(s) < 100:
            parts = [p.strip() for p in s.split('|', 1)]
            _add_two_col_line(doc, parts[0], parts[1] if len(parts) > 1 else '', left_bold=True)
            continue

        # Regular body text
        _add_body(doc, s)

    doc.save(output_path)
    return output_path