import os
import resend


def send_resume_email(
    user,
    pdf_path,
    ats_score,
    job_title,
    matched_skills,
    missing_skills
):
    matched_html = "".join(
        f"<li style='margin-bottom:4px'>{s}</li>"
        for s in matched_skills[:10]
    ) or "<li>None detected</li>"

    missing_html = "".join(
        f"<li style='margin-bottom:4px'>{s}</li>"
        for s in missing_skills[:10]
    ) or "<li>None — great match!</li>"

    score_color = (
        "#10b981"
        if ats_score >= 80
        else "#f59e0b"
        if ats_score >= 60
        else "#ef4444"
    )

    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;padding:32px;color:#1e293b">
      <h2 style="color:#4f46e5;margin-bottom:4px">
        Your Optimized Resume is Ready! ✨
      </h2>

      <p style="color:#64748b;margin-top:0">
        Job Title: <strong>{job_title}</strong>
      </p>

      <div style="background:#f8fafc;border-radius:12px;padding:20px;margin:20px 0;text-align:center">
        <div style="font-size:42px;font-weight:800;color:{score_color}">
          {ats_score:.0f}%
        </div>
        <div style="color:#64748b;font-size:13px;text-transform:uppercase;letter-spacing:0.05em">
          ATS Compatibility Score
        </div>
      </div>

      <table style="width:100%;border-collapse:collapse;margin-bottom:20px">
        <tr>
          <td style="vertical-align:top;width:50%;padding-right:12px">
            <h4 style="color:#065f46;margin-bottom:8px">
              ✅ Matched Skills
            </h4>
            <ul style="padding-left:18px;margin:0;color:#334155;font-size:14px">
              {matched_html}
            </ul>
          </td>

          <td style="vertical-align:top;width:50%;padding-left:12px">
            <h4 style="color:#991b1b;margin-bottom:8px">
              ❌ Missing Skills
            </h4>
            <ul style="padding-left:18px;margin:0;color:#334155;font-size:14px">
              {missing_html}
            </ul>
          </td>
        </tr>
      </table>

      <p style="color:#475569;line-height:1.6">
        Your AI-optimized resume is attached as a PDF — ready to send to employers.
        Log back into ResumeAI anytime to view your full history or chat with the AI Career Coach.
      </p>

      <p style="color:#94a3b8;font-size:12px;margin-top:32px">
        This email was sent automatically because you requested your optimized resume from ResumeAI.
      </p>
    </div>
    """

    try:
        resend.api_key = os.getenv("RESEND_API_KEY")

        if not resend.api_key:
            raise RuntimeError("RESEND_API_KEY is not configured.")

        print(f"[EMAIL] Preparing resume email for {user.email}")

        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        params = {
            "from": "onboarding@resend.dev",
            "to": [user.email],
            "subject": (
                f"Your Optimized Resume — "
                f"{job_title} ({ats_score:.0f}% ATS Score)"
            ),
            "html": html_body,
            "attachments": [
                {
                    "filename": os.path.basename(pdf_path),
                    "content": pdf_data,
                }
            ],
        }

        response = resend.Emails.send(params)

        print(f"[EMAIL] Resend response: {response}")
        print(f"[EMAIL] Resume email sent successfully to {user.email}")

    except Exception as e:
        print(f"[EMAIL ERROR] Resend failed: {e}")
        raise