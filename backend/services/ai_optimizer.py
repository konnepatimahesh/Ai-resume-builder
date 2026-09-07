import os
import re
from groq import Groq

def optimize_resume(resume_text, job_description, missing_skills):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    missing_str = ", ".join(missing_skills) if missing_skills else "none"
    prompt = (
        "You are an expert resume writer. Rewrite and optimize the resume below to match the job description.\n\n"
        "RULES:\n"
        "1. Keep the exact same section headers and order as the original resume.\n"
        "2. Write each section header in ALL CAPS on its own line.\n"
        "3. After each section header, add a line with only: ---\n"
        "4. Keep all factual info (companies, dates, degrees) unchanged.\n"
        "5. Incorporate these missing keywords naturally: " + missing_str + "\n"
        "6. Start bullet points with strong action verbs and use bullet symbol.\n"
        "7. Output ONLY the resume text. No thinking, no explanation, no stars, no markdown.\n\n"
        "JOB DESCRIPTION:\n" + job_description[:3000] + "\n\n"
        "ORIGINAL RESUME:\n" + resume_text[:4000] + "\n\n"
        "Now write the optimized resume:"
    )
    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2500,
        temperature=0.5,
        reasoning_effort="none",
    )
    reply = response.choices[0].message.content
    reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()
    reply = re.sub(r'\*{1,3}', '', reply)
    return reply