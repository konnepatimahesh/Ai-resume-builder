
from fpdf import FPDF
import os, re

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")

_SAFE_RANGES = [(0x0020,0x007E),(0x00A0,0x024F),(0x0370,0x03FF),(0x0400,0x04FF),(0x2010,0x2027)]

def _safe(t):
    return "".join(c if any(s<=ord(c)<=e for s,e in _SAFE_RANGES) else '' for c in t)

def _clean(text):
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'\*{1,3}', '', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    return text.strip()

def generate_pdf(optimized_text, output_path):
    text = _clean(optimized_text)
    lines = text.split('\n')

    gh = re.search(r'github\.com/([\w\-]+)', text, re.IGNORECASE)
    li = re.search(r'linkedin\.com/in/([\w\-]+)', text, re.IGNORECASE)
    github_url   = 'https://' + gh.group(0) if gh else None
    linkedin_url = 'https://' + li.group(0) if li else None

    pdf = FPDF()
    pdf.set_margins(14, 11, 14)
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=9)
    pdf.add_font("R", "",  os.path.join(FONT_DIR, "DejaVuSans.ttf"),      uni=True)
    pdf.add_font("R", "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"), uni=True)

    header_done = False
    name_done   = False

    for raw in lines:
        s = raw.strip()
        if not s:
            pdf.ln(1)
            continue
        line = _safe(s)
        if not line:
            continue

        # Section divider
        if re.fullmatch(r'-{2,}', s):
            header_done = True
            y = pdf.get_y()
            pdf.set_draw_color(150,150,150)
            pdf.set_line_width(0.3)
            pdf.line(pdf.l_margin, y, pdf.w-pdf.r_margin, y)
            pdf.ln(1.5)
            continue

        # Section header
        is_sec = s.isupper() and 2<=len(s)<45 and any(c.isalpha() for c in s)
        if is_sec:
            header_done = True
            pdf.ln(1.5)
            pdf.set_font("R","B",9)
            pdf.set_x(pdf.l_margin)
            pdf.cell(0, 5, line, ln=True)
            continue

        # Name — centered, bold, large
        if not name_done:
            name_done = True
            pdf.set_font("R","B",13)
            pdf.cell(0, 7, line, align='C', ln=True)
            continue

        # Contact lines — split into two shorter lines + hyperlinks
        if not header_done:
            pdf.set_font("R","",7.5)
            pdf.set_text_color(50,50,50)

            # Replace raw URLs with short labels
            display = line
            if github_url:
                display = re.sub(r'Github\s*:\s*github\.com/[\w\-]+', 'GitHub', display, flags=re.IGNORECASE)
                display = re.sub(r'github\.com/[\w\-]+', 'GitHub', display, flags=re.IGNORECASE)
            if linkedin_url:
                display = re.sub(r'Linkedin\s*:\s*linkedin\.com/in/[\w\-]+', 'LinkedIn', display, flags=re.IGNORECASE)
                display = re.sub(r'linkedin\.com/in/[\w\-]+', 'LinkedIn', display, flags=re.IGNORECASE)

            page_w = pdf.w - pdf.l_margin - pdf.r_margin
            line_w = pdf.get_string_width(display)
            start_x = pdf.l_margin + (page_w - line_w) / 2
            y0 = pdf.get_y()

            pdf.cell(0, 4.5, display, align='C', ln=True)

            # Clickable GitHub
            if github_url and 'GitHub' in display:
                pre = display[:display.index('GitHub')]
                gx = start_x + pdf.get_string_width(pre)
                gw = pdf.get_string_width('GitHub')
                pdf.link(gx, y0, gw, 4.5, github_url)

            # Clickable LinkedIn
            if linkedin_url and 'LinkedIn' in display:
                pre = display[:display.index('LinkedIn')]
                lx = start_x + pdf.get_string_width(pre)
                lw = pdf.get_string_width('LinkedIn')
                pdf.link(lx, y0, lw, 4.5, linkedin_url)

            pdf.set_text_color(0,0,0)
            continue

        # Bullet
        if s.startswith(('•','-','*')) and len(s)>2:
            bt = re.sub(r'^[•\-\*]\s*','', line).strip()
            bt = re.sub(r'\bLink\b\s*$','', bt).strip()
            if bt:
                pdf.set_font("R","",8.3)
                pdf.set_x(pdf.l_margin+3)
                w = pdf.w - pdf.l_margin - pdf.r_margin - 3
                pdf.multi_cell(w, 4.3, '• '+bt)
            continue

        # Job/project title with date
        dm = re.search(
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}'
            r'\s*[-–]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|present|\d{4}))',
            line)
        if dm or '|' in line:
            if dm:
                ds = dm.group(1).strip()
                ls = line[:dm.start()].strip().rstrip('|').strip()
                lw = pdf.w - pdf.l_margin - pdf.r_margin - 30
                pdf.set_font("R","B",8.5)
                pdf.set_x(pdf.l_margin)
                pdf.cell(lw, 5, _safe(ls))
                pdf.set_font("R","",7.5)
                pdf.set_text_color(70,70,70)
                pdf.cell(30, 5, _safe(ds), align='R')
                pdf.ln(5)
                pdf.set_text_color(0,0,0)
            else:
                pdf.set_font("R","B",8.5)
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 5, _safe(line))
            continue

        # Body text
        pdf.set_font("R","",8.3)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 4.5, line)

    pdf.output(output_path)
    return output_path
