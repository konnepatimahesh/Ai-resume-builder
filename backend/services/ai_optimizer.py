import os
import re
from groq import Groq

def optimize_resume(resume_text, job_description, missing_skills):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    missing_str = ", ".join(missing_skills) if missing_skills else "none"

    prompt = (
        "You are an expert ATS-optimized resume writer. Rewrite the resume below to perfectly match the job description.\n\n"
        "STRICT FORMAT RULES — follow exactly:\n"
        "1. First line: Candidate's full name only (e.g. John Smith)\n"
        "2. Second line: Contact info separated by  |  (e.g. john@email.com | +1-555-0100 | linkedin.com/in/john | github.com/john)\n"
        "3. Third line: Must be exactly: ---\n"
        "4. Each section header: ALL CAPS on its own line (e.g. PROFESSIONAL SUMMARY)\n"
        "5. After each section header: a line with exactly: ---\n"
        "6. Bullet points: start with • (bullet symbol), one per line\n"
        "7. Job entries: format as  'Company Name | Job Title  Month YYYY – Month YYYY'\n"
        "8. Education entries: format as 'University Name | Degree  Month YYYY – Month YYYY'\n"
        "9. Skills section: list skills as comma-separated on one line or grouped by category\n"
        "10. DO NOT use markdown (**bold**, ## headers, etc.)\n"
        "11. DO NOT add any commentary, preamble, or notes\n"
        "12. Incorporate these missing keywords naturally: " + missing_str + "\n"
        "13. Keep all factual details (companies, dates, degrees, GPA) UNCHANGED\n"
        "14. Use strong action verbs for all bullet points\n"
        "15. Aim for a complete, professional resume — do not cut off\n\n"
        "JOB DESCRIPTION:\n" + job_description[:3000] + "\n\n"
        "ORIGINAL RESUME:\n" + resume_text[:4000] + "\n\n"
        "Write the complete optimized resume now:"
    )

    # Models verified available on this account — best quality first
    models_to_try = [
        "qwen/qwen3.8-27b",
        "qwen/qwen3.6-27b",
        "openai/gpt-oss-120b",
    ]

    last_error = None
    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.4,
            )
            reply = response.choices[0].message.content
            # Strip any thinking tags or markdown
            reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()
            reply = re.sub(r'\*{1,3}', '', reply)
            reply = re.sub(r'^#{1,6}\s*', '', reply, flags=re.MULTILINE)
            return reply
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"All Groq models failed. Last error: {last_error}")