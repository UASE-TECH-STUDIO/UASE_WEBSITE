import logging
import os

logger = logging.getLogger(__name__)

BRAND_COLOR = "#e8a045"
DARK_BG = "#06080f"


def _get_resend():
    """Import resend and set API key fresh each call — safe if package missing."""
    try:
        import resend
        from django.conf import settings
        api_key = getattr(settings, "RESEND_API_KEY", None) or os.environ.get("RESEND_API_KEY")
        if not api_key:
            raise ValueError("RESEND_API_KEY is not set in environment variables.")
        resend.api_key = api_key
        return resend
    except ImportError:
        raise RuntimeError("resend package is not installed. Run: pip install resend")


def _base_html(title: str, body_content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#f4f5f7;font-family:'Segoe UI',Arial,sans-serif;color:#1a1a2e;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f5f7;padding:32px 16px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
        <tr>
          <td style="background:{DARK_BG};padding:24px 32px;text-align:center;">
            <span style="display:inline-block;background:{BRAND_COLOR};width:34px;height:34px;border-radius:8px;text-align:center;line-height:34px;font-weight:900;color:#000;font-size:13px;font-family:monospace;vertical-align:middle;">U</span>
            &nbsp;
            <span style="color:#fff;font-size:17px;font-weight:800;vertical-align:middle;">UASE <span style="color:{BRAND_COLOR};">Tech Studio</span></span>
          </td>
        </tr>
        <tr><td style="padding:32px;">{body_content}</td></tr>
        <tr>
          <td style="background:#f8f9fb;padding:18px 32px;border-top:1px solid #eee;text-align:center;">
            <p style="margin:0 0 4px;font-size:12px;color:#888;">
              <a href="https://uase.tech" style="color:{BRAND_COLOR};text-decoration:none;font-weight:600;">uase.tech</a>
              &nbsp;&bull;&nbsp;
              <a href="mailto:uasetechstudio@gmail.com" style="color:#888;text-decoration:none;">uasetechstudio@gmail.com</a>
              &nbsp;&bull;&nbsp;
              <a href="https://wa.me/2349133549399" style="color:#888;text-decoration:none;">WhatsApp</a>
            </p>
            <p style="margin:0;font-size:11px;color:#aaa;">&copy; 2026 UASE Tech Studio. All rights reserved.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_admin_notification(data: dict) -> None:
    """Notify admin when a contact form is submitted."""
    resend = _get_resend()
    from django.conf import settings

    recipient = getattr(settings, "CONTACT_RECIPIENT_EMAIL", None) or os.environ.get(
        "CONTACT_RECIPIENT_EMAIL", "uasetechstudio@gmail.com"
    )

    body = f"""
    <h2 style="margin:0 0 6px;font-size:20px;font-weight:800;color:#0f1117;">New Project Enquiry</h2>
    <p style="margin:0 0 20px;color:#666;font-size:14px;">Someone submitted the contact form on uase.tech.</p>

    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f9fb;border:1px solid #eee;border-radius:10px;margin-bottom:20px;">
      <tr><td style="padding:18px 20px;">
        <p style="margin:0 0 4px;font-size:11px;color:#aaa;text-transform:uppercase;letter-spacing:0.08em;">From</p>
        <p style="margin:0 0 2px;font-size:18px;font-weight:700;color:#0f1117;">{data.get('name','')}</p>
        <a href="mailto:{data.get('email','')}" style="color:{BRAND_COLOR};font-size:14px;">{data.get('email','')}</a>
      </td></tr>
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
      <tr>
        <td width="50%" style="padding-right:6px;">
          <div style="background:#f8f9fb;border:1px solid #eee;border-radius:8px;padding:12px 16px;">
            <p style="margin:0 0 3px;font-size:10px;color:#aaa;text-transform:uppercase;">Subject</p>
            <p style="margin:0;font-size:13px;font-weight:600;color:#0f1117;">{data.get('subject','No Subject')}</p>
          </div>
        </td>
        <td width="50%" style="padding-left:6px;">
          <div style="background:#f8f9fb;border:1px solid #eee;border-radius:8px;padding:12px 16px;">
            <p style="margin:0 0 3px;font-size:10px;color:#aaa;text-transform:uppercase;">Budget</p>
            <p style="margin:0;font-size:13px;font-weight:600;color:#0f1117;">{data.get('budget','Not specified')}</p>
          </div>
        </td>
      </tr>
    </table>

    <div style="background:#f8f9fb;border:1px solid #eee;border-left:3px solid {BRAND_COLOR};border-radius:8px;padding:18px 20px;margin-bottom:24px;">
      <p style="margin:0 0 8px;font-size:10px;color:#aaa;text-transform:uppercase;">Message</p>
      <p style="margin:0;font-size:14px;color:#333;line-height:1.7;white-space:pre-wrap;">{data.get('message','')}</p>
    </div>

    <table width="100%" cellpadding="0" cellspacing="0">
      <tr><td align="center">
        <a href="mailto:{data.get('email','')}?subject=Re: {data.get('subject','Your Enquiry')}&body=Hello {data.get('name','')},%0A%0A"
           style="display:inline-block;background:{BRAND_COLOR};color:#000;padding:13px 28px;border-radius:8px;font-weight:700;text-decoration:none;font-size:14px;">
          Reply to {data.get('name','')} &rarr;
        </a>
      </td></tr>
    </table>
    """

    resend.Emails.send({
        "from": "UASE Tech Studio <onboarding@resend.dev>",
        "to": [recipient],
        "reply_to": data.get("email", ""),
        "subject": f"[New Enquiry] {data.get('subject','Contact Form')} — from {data.get('name','')}",
        "html": _base_html(f"New Enquiry from {data.get('name','')}", body),
    })
    logger.info(f"Admin notification sent for enquiry from {data.get('email','')}")


def send_user_confirmation(name: str, email: str, subject: str = "") -> None:
    """Send a confirmation email to the person who submitted the form."""
    resend = _get_resend()
    first = name.strip().split()[0] if name.strip() else name

    body = f"""
    <h2 style="margin:0 0 8px;font-size:20px;font-weight:800;color:#0f1117;">We got your message, {first}.</h2>
    <p style="margin:0 0 20px;color:#666;font-size:14px;line-height:1.7;">
      Thank you for reaching out to <strong>UASE Tech Studio</strong>. We take every enquiry seriously —
      expect a personal response within <strong>24 hours</strong>.
    </p>

    <div style="background:#f8f9fb;border:1px solid #eee;border-radius:10px;padding:20px;margin-bottom:20px;">
      <p style="margin:0 0 14px;font-size:11px;font-weight:700;text-transform:uppercase;color:#aaa;">What happens next</p>
      <p style="margin:0 0 10px;font-size:13px;color:#333;"><span style="background:{BRAND_COLOR};color:#000;width:22px;height:22px;border-radius:50%;display:inline-block;text-align:center;line-height:22px;font-size:10px;font-weight:800;margin-right:10px;">1</span>We review your message and project requirements</p>
      <p style="margin:0 0 10px;font-size:13px;color:#333;"><span style="background:{BRAND_COLOR};color:#000;width:22px;height:22px;border-radius:50%;display:inline-block;text-align:center;line-height:22px;font-size:10px;font-weight:800;margin-right:10px;">2</span>Usty reaches out to discuss your goals in detail</p>
      <p style="margin:0;font-size:13px;color:#333;"><span style="background:{BRAND_COLOR};color:#000;width:22px;height:22px;border-radius:50%;display:inline-block;text-align:center;line-height:22px;font-size:10px;font-weight:800;margin-right:10px;">3</span>We architect a solution and share a clear proposal</p>
    </div>

    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
      <tr>
        <td width="50%" style="padding-right:6px;">
          <a href="https://uase.tech/portfolio/" style="display:block;text-align:center;background:#f8f9fb;border:1px solid #eee;border-radius:8px;padding:12px;text-decoration:none;color:#333;font-size:12px;font-weight:600;">View Portfolio</a>
        </td>
        <td width="50%" style="padding-left:6px;">
          <a href="https://carstrims-app.vercel.app/" style="display:block;text-align:center;background:#f8f9fb;border:1px solid #eee;border-radius:8px;padding:12px;text-decoration:none;color:#333;font-size:12px;font-weight:600;">&#9889; See CARSTRIMS Live</a>
        </td>
      </tr>
    </table>

    <p style="margin:0;color:#888;font-size:12px;line-height:1.7;">
      For urgent enquiries, WhatsApp us directly:
      <a href="https://wa.me/2349133549399" style="color:{BRAND_COLOR};font-weight:600;">+234 913 354 9399</a>
    </p>
    """

    resend.Emails.send({
        "from": "UASE Tech Studio <onboarding@resend.dev>",
        "to": [email],
        "reply_to": "uasetechstudio@gmail.com",
        "subject": "We received your message — UASE Tech Studio",
        "html": _base_html(f"Message received, {first}!", body),
    })
    logger.info(f"Confirmation email sent to {email}")


def send_admin_reply(to_email: str, name: str, message: str) -> None:
    """Send a direct reply from admin to a client."""
    resend = _get_resend()
    first = name.strip().split()[0] if name.strip() else name

    body = f"""
    <h2 style="margin:0 0 8px;font-size:20px;font-weight:800;color:#0f1117;">Hello {first},</h2>
    <p style="margin:0 0 20px;color:#666;font-size:14px;">A message from UASE Tech Studio:</p>
    <div style="background:#f8f9fb;border:1px solid #eee;border-left:3px solid {BRAND_COLOR};border-radius:8px;padding:18px 20px;margin-bottom:24px;">
      <p style="margin:0;font-size:14px;color:#333;line-height:1.75;white-space:pre-wrap;">{message}</p>
    </div>
    <p style="margin:0;color:#888;font-size:12px;">
      Reply to this email or WhatsApp us:
      <a href="https://wa.me/2349133549399" style="color:{BRAND_COLOR};font-weight:600;">+234 913 354 9399</a>
    </p>
    """

    resend.Emails.send({
        "from": "UASE Tech Studio <onboarding@resend.dev>",
        "to": [to_email],
        "reply_to": "uasetechstudio@gmail.com",
        "subject": "Reply from UASE Tech Studio",
        "html": _base_html(f"Reply for {name}", body),
    })
