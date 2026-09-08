"""
Professional resume PDF generator using fpdf2.
Produces a clean, ATS-compatible, visually polished resume.
"""
from fpdf import FPDF
import os
import re

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")

# Safe character range — strips truly unrenderable chars
_SAFE_RANGES = [(0x0020, 0x007E), (0x00A0, 0x024F), (0x0370, 0x03FF),
                (0x0400, 0x04FF), (0x2010, 0x2027)]

def _safe(t):
    return "".join(c if any(s <= ord(c) <= e for s, e in _SAFE_RANGES) else '' for c in str(t))

def _clean_text(text):
    """Remove AI artefacts — think-tags, markdown stars, hash headers."""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'\*{1,3}', '', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    # Normalize bullet chars
    text = re.sub(r'^[\-\*]\s+', '• ', text, flags=re.MULTILINE)
    return text.strip()


def generate_pdf(optimized_text, output_path):
    text = _clean_text(optimized_text)
    lines = [l.rstrip() for l in text.split('\n')]

    # Extract hyperlink targets
    gh = re.search(r'github\.com/([\w\-]+(?:/[\w\-]+)?)', text, re.IGNORECASE)
    li = re.search(r'linkedin\.com/in/([\w\-]+)', text, re.IGNORECASE)
    github_url   = 'https://' + gh.group(0) if gh else None
    linkedin_url = 'https://' + li.group(0) if li else None

    # ── Page setup ──────────────────────────────────────────────────────────
    pdf = FPDF(format='Letter')
    pdf.set_margins(left=17, top=14, right=17)
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    # Fonts
    regular = os.path.join(FONT_DIR, "DejaVuSans.ttf")
    bold    = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
    pdf.add_font("R", "",  regular, uni=True)
    pdf.add_font("R", "B", bold,    uni=True)

    # ── Color palette ────────────────────────────────────────────────────────
    ACCENT   = (31, 78, 121)    # dark navy blue — section headers
    DARK     = (30, 30, 30)     # near-black for body text
    MID      = (80, 80, 80)     # medium gray for dates / sub-info
    RULE_CLR = (180, 180, 180)  # light rule lines

    # ── State ────────────────────────────────────────────────────────────────
    name_done      = False   # first non-blank line = name
    contact_done   = False   # second block = contact (until first ---)
    in_section     = False   # we've passed the header block

    USABLE_W = pdf.w - pdf.l_margin - pdf.r_margin

    # ── Date pattern for two-column job/edu lines ────────────────────────────
    DATE_RE = re.compile(
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}'
        r'\s*[–\-—]\s*'
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec[a-z]*\.?\s+\d{4}|Present|Current|Now|\d{4}))',
        re.IGNORECASE
    )

    def draw_rule(y_offset=0.5):
        y = pdf.get_y() + y_offset
        pdf.set_draw_color(*RULE_CLR)
        pdf.set_line_width(0.25)
        pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
        pdf.set_y(y + 1.5)

    def centered_text(text_str, font_size, bold_flag=False, color=DARK, line_h=5.5):
        pdf.set_font("R", "B" if bold_flag else "", font_size)
        pdf.set_text_color(*color)
        pdf.set_x(pdf.l_margin)
        pdf.cell(USABLE_W, line_h, _safe(text_str), align='C', ln=True)

    def section_header(text_str):
        pdf.ln(3)
        pdf.set_font("R", "B", 8.8)
        pdf.set_text_color(*ACCENT)
        pdf.set_x(pdf.l_margin)
        pdf.cell(USABLE_W, 5.5, _safe(text_str.upper()), ln=True)
        draw_rule(0)
        pdf.set_text_color(*DARK)

    def bullet_line(text_str):
        clean = re.sub(r'^[•\-\*]\s*', '', text_str).strip()
        if not clean:
            return
        pdf.set_font("R", "", 8.5)
        pdf.set_text_color(*DARK)
        # Bullet indent
        INDENT = 5
        pdf.set_x(pdf.l_margin + INDENT)
        w = USABLE_W - INDENT
        pdf.multi_cell(w, 4.6, _safe('• ' + clean))

    def two_col_line(left_str, right_str, left_bold=True):
        """Render left part bold, right part right-aligned in gray."""
        DATE_COL = 38
        left_w   = USABLE_W - DATE_COL
        pdf.set_x(pdf.l_margin)
        if left_bold:
            pdf.set_font("R", "B", 8.8)
        else:
            pdf.set_font("R", "", 8.5)
        pdf.set_text_color(*DARK)
        pdf.cell(left_w, 5.2, _safe(left_str), ln=False)
        pdf.set_font("R", "", 8.0)
        pdf.set_text_color(*MID)
        pdf.cell(DATE_COL, 5.2, _safe(right_str), align='R', ln=True)
        pdf.set_text_color(*DARK)

    def body_line(text_str):
        pdf.set_font("R", "", 8.5)
        pdf.set_text_color(*DARK)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(USABLE_W, 4.8, _safe(text_str))

    # ── Main render loop ─────────────────────────────────────────────────────
    for raw in lines:
        s = raw.strip()

        # Skip blank lines gracefully
        if not s:
            pdf.ln(1.2)
            continue

        # ── Divider line --- ──────────────────────────────────────────────────
        if re.fullmatch(r'-{2,}', s):
            if not contact_done:
                contact_done = True   # first --- ends the contact block
            draw_rule(0.2)
            in_section = True
            continue

        # ── Name (very first non-blank line) ─────────────────────────────────
        if not name_done:
            name_done = True
            pdf.set_font("R", "B", 18)
            pdf.set_text_color(*ACCENT)
            pdf.set_x(pdf.l_margin)
            pdf.cell(USABLE_W, 10, _safe(s), align='C', ln=True)
            pdf.set_text_color(*DARK)
            continue

        # ── Contact lines (before first ---) ─────────────────────────────────
        if not contact_done:
            pdf.set_font("R", "", 8.0)
            pdf.set_text_color(*MID)

            # Split on | and render with hyperlinks
            parts = [p.strip() for p in s.split('|')]
            display_parts = []
            for p in parts:
                if 'github.com' in p.lower():
                    display_parts.append('github.com/' + gh.group(1) if gh else p)
                elif 'linkedin.com' in p.lower():
                    display_parts.append('linkedin.com/in/' + li.group(1) if li else p)
                else:
                    display_parts.append(p)

            display = '  |  '.join(display_parts)
            display = _safe(display)

            # Render centered
            lw = pdf.get_string_width(display)
            x0 = pdf.l_margin + (USABLE_W - lw) / 2
            y0 = pdf.get_y()
            pdf.set_x(pdf.l_margin)
            pdf.cell(USABLE_W, 4.8, display, align='C', ln=True)

            # Add hyperlinks
            if github_url and gh:
                anchor_text = 'github.com/' + gh.group(1)
                idx = display.find(anchor_text)
                if idx >= 0:
                    pre_w = pdf.get_string_width(display[:idx])
                    lnk_w = pdf.get_string_width(anchor_text)
                    pdf.link(x0 + pre_w, y0, lnk_w, 4.8, github_url)

            if linkedin_url and li:
                anchor_text = 'linkedin.com/in/' + li.group(1)
                idx = display.find(anchor_text)
                if idx >= 0:
                    pre_w = pdf.get_string_width(display[:idx])
                    lnk_w = pdf.get_string_width(anchor_text)
                    pdf.link(x0 + pre_w, y0, lnk_w, 4.8, linkedin_url)

            pdf.set_text_color(*DARK)
            continue

        # ── Section header: ALL CAPS short line ───────────────────────────────
        if (s.isupper() and 2 <= len(s) <= 50
                and any(c.isalpha() for c in s)
                and not re.search(r'\d{4}', s)):
            section_header(s)
            continue

        # ── Bullet point ──────────────────────────────────────────────────────
        if s.startswith(('•', '-', '*')) and len(s) > 2:
            bullet_line(s)
            continue

        # ── Two-column line: has date range ──────────────────────────────────
        dm = DATE_RE.search(s)
        if dm:
            date_str  = dm.group(1).strip()
            left_str  = s[:dm.start()].strip().rstrip('|–-').strip()
            # Detect if this is a sub-line (company only, italic feel)
            is_title_line = '|' in left_str or len(left_str) < 60
            two_col_line(left_str, date_str, left_bold=True)
            continue

        # ── Pipe-separated line (Company | Role) without date ─────────────────
        if '|' in s and len(s) < 100:
            parts = [p.strip() for p in s.split('|', 1)]
            pdf.set_font("R", "B", 8.8)
            pdf.set_text_color(*DARK)
            pdf.set_x(pdf.l_margin)
            if len(parts) == 2:
                half = USABLE_W / 2
                pdf.cell(half, 5.2, _safe(parts[0]), ln=False)
                pdf.set_font("R", "", 8.5)
                pdf.set_text_color(*MID)
                pdf.cell(half, 5.2, _safe(parts[1]), align='R', ln=True)
            else:
                pdf.cell(USABLE_W, 5.2, _safe(s), ln=True)
            pdf.set_text_color(*DARK)
            continue

        # ── Regular body text ─────────────────────────────────────────────────
        body_line(s)

    pdf.output(output_path)
    return output_path