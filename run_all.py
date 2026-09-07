import os
import sys

# Ensure our local directory modules are prioritized
sys.path.insert(0, '.')

project_root = os.getcwd()
fonts_dir = os.path.join(project_root, 'fonts')
output_pdf = os.path.join(project_root, 'clean_resume.pdf')
output_png = os.path.join(project_root, 'clean_page-1.png')

import pdf_generator
pdf_generator.FONT_DIR = fonts_dir

sample = """KONNEPATI MAHESH
Nellore, Andhra Pradesh | +91 7989704550 | vkonnepati36@jnn.edu.in
Github : ://github.com | Linkedin : ://linkedin.com

SUMMARY
---
Final-year B.Tech graduate in Artificial Intelligence and Data Science seeking a Python Developer role. Experienced in building scalable Python-based web applications, RESTful APIs, and database-driven systems using Flask, OpenCV, and MySQL. Skilled in backend architecture, data pipelines, and deploying AI/ML solutions with PostgreSQL and MongoDB. Strong problem-solving skills with focus on clean, efficient software.

EDUCATION
---
B.Tech - Artificial Intelligence & Data Science | Oct 2022 - May 2026
J.N.N Institute of Engineering | CGPA: 8.17 / 10

Intermediate (MPC) | Jun 2020 - Mar 2022
Vignan College | CGPA: 6.5 / 10

SSC (10th Grade) | Jun 2019 - Mar 2020
Z.P.P. High School | GPA: 9.2 / 10

SKILLS
---
Programming Languages: Python, Java, JavaScript
Backend: Flask, RESTful APIs, REST API Development, PostgreSQL, MongoDB
AI / ML Libraries: OpenCV, MediaPipe, NumPy, Pandas
Database: MySQL, PostgreSQL, MongoDB
Version Control: Git, GitHub
Frontend: HTML5, CSS3, Figma, Canva
Visualization Tools: Power BI, MS Excel

WORK EXPERIENCE
---
AI Developer Intern | Edunet Foundation (IBM SKILLS BUILD) | Jul 2024 - Aug 2024
- Developed an AI-powered event assistance chatbot using Python, improving student access to college event details and reducing manual queries by 40%.
- Built interactive dashboards in Power BI to analyze agriculture datasets, enabling data-driven business decisions.
- Deployed application components on IBM Cloud and collaborated with cross-functional teams in an agile environment.

PROJECTS
---
AI Attendance Tracker | Python, Flask, OpenCV, MySQL | Sep 2025 - Oct 2025
- Developed a web-based face recognition attendance system using Python, Flask, and OpenCV with real-time webcam input, achieving 85% recognition accuracy.
- Integrated MySQL and PostgreSQL databases for storing facial feature data with a modular, scalable backend architecture.
- Automated the full attendance pipeline, eliminating manual tracking entirely.

Sign Language Translator | Python, OpenCV, MediaPipe, TTS | Dec 2024 - Jan 2025
- Built a real-time sign language recognition system using Python, OpenCV, and MediaPipe to detect hand gestures via live webcam.
- Integrated a text-to-speech pipeline to convert recognized gestures into audio output.
- Designed a modular classification pipeline with clean separation of layers.

PUBLICATIONS
---
- A Synergistic Approach to Real-Time Text Translation and Speech Synthesis - Research on integrating machine translation with text-to-speech systems for multilingual accessibility.

CERTIFICATIONS
---
- Introduction to Artificial Intelligence - Infosys Springboard
- Data Science with Python - Simplilearn
"""

print("1. Compiling resume to PDF...")
pdf_generator.generate_pdf(sample, output_pdf)
print(f"   -> Success! Generated PDF ({os.path.getsize(output_pdf)} bytes)")

print("2. Converting PDF page to PNG preview image...")
import pymupdf
doc = pymupdf.open(output_pdf)
page = doc.load_page(0)
pix = page.get_pixmap(dpi=120)
pix.save(output_png)
print(f"   -> Success! Preview image saved at: {output_png}")
