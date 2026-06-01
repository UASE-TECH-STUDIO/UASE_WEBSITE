import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY

BRAND_COLOR = "#e8a045"
DARK_BG = "#06080f"
SURFACE = "#111827"


def _base_html(title: str, body_content: str) -> str:
    """Shared branded HTML wrapper for all emails."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#f4f5f7;font-family:'Segoe UI',Arial,sans-serif;color:#1a1a2e;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f5f7;padding:32px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

        <!-- HEADER -->
        <tr>
          <td style="background:{DARK_BG};padding:28px 36px;text-align:center;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td align="center">
                  <span style="display:inline-block;background:{BRAND_COLOR};width:36px;height:36px;border-radius:8px;text-align:center;line-height:36px;font-weight:900;color:#000;font-size:14px;font-family:monospace;vertical-align:middle;">U</span>
                  &nbsp;
                  <span style="color:#ffffff;font-size:18px;font-weight:800;vertical-align:middle;letter-spacing:0.02em;">UASE <span style="color:{BRAND_COLOR};">Tech Studio</span></span>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- BODY -->
        <tr>
          <td style="padding:36px 36px 24px;">
            {body_content}
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td style="background:#f8f9fb;padding:20px 36px;border-top:1px solid #eee;text-align:center;">
            <p style="margin:0 0 6px;font-size:12px;color:#888;">
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
    """
    Sends a rich notification email to admin when a contact form is submitted.
    """
    urgency_color = "#e74c3c" if "urgent" in data.get("subject", "").lower() else BRAND_COLOR

    body = f"""
    <h2 style="margin:0 0 6px;font-size:22px;font-weight:800;color:#0f1117;">New Project Enquiry</h2>
    <p style="margin:0 0 24px;color:#666;font-size:14px;">Someone just sent a message via the UASE Tech Studio contact form.</p>

    <!-- Sender card -->
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f9fb;border:1px solid #eee;border-radius:12px;padding:0;margin-bottom:24px;">
      <tr>
        <td style="padding:20px 24px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td>
                <p style="margin:0 0 4px;font-size:11px;color:#aaa;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;">From</p>
                <p style="margin:0;font-size:18px;font-weight:700;color:#0f1117;">{data['name']}</p>
                <a href="mailto:{data['email']}" style="color:{BRAND_COLOR};font-size:14px;text-decoration:none;">{data['email']}</a>
              </td>
              <td align="right" style="vertical-align:top;">
                <span style="background:{urgency_color}15;color:{urgency_color};padding:4px 12px;border-radius:100px;font-size:11px;font-weight:700;font-family:monospace;border:1px solid {urgency_color}40;">ENQUIRY</span>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>

    <!-- Meta info -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
      <tr>
        <td width="50%" style="padding-right:8px;">
          <div style="background:#f8f9fb;border:1px solid #eee;border-radius:10px;padding:14px 18px;">
            <p style="margin:0 0 3px;font-size:10px;color:#aaa;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;">Subject</p>
            <p style="margin:0;font-size:14px;font-weight:600;color:#0f1117;">{data.get('subject', 'No Subject')}</p>
          </div>
        </td>
        <td width="50%" style="padding-left:8px;">
          <div style="background:#f8f9fb;border:1px solid #eee;border-radius:10px;padding:14px 18px;">
            <p style="margin:0 0 3px;font-size:10px;color:#aaa;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;">Location</p>
            <p style="margin:0;font-size:14px;font-weight:600;color:#0f1117;">{data.get('country', 'Unknown')}</p>
          </div>
        </td>
      </tr>
    </table>

    <!-- Message -->
    <div style="background:#f8f9fb;border:1px solid #eee;border-left:3px solid {BRAND_COLOR};border-radius:10px;padding:20px 24px;margin-bottom:28px;">
      <p style="margin:0 0 8px;font-size:11px;color:#aaa;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;">Message</p>
      <p style="margin:0;font-size:15px;color:#333;line-height:1.7;white-space:pre-wrap;">{data['message']}</p>
    </div>

    <!-- CTA -->
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td align="center">
          <a href="mailto:{data['email']}?subject=Re: {data.get('subject','Your Enquiry')}&body=Hello {data['name']},%0A%0A"
             style="display:inline-block;background:{BRAND_COLOR};color:#000;padding:14px 32px;border-radius:10px;font-weight:700;text-decoration:none;font-size:15px;">
            Reply to {data['name']} &rarr;
          </a>
        </td>
      </tr>
    </table>
    """
    resend.Emails.send({
        "from": "UASE Tech Studio <onboarding@resend.dev>",
        "to": [settings.CONTACT_RECIPIENT_EMAIL or "uasetechstudio@gmail.com"],
        "reply_to": data["email"],
        "subject": f"[New Enquiry] {data.get('subject', 'Contact Form')} — from {data['name']}",
        "html": _base_html(f"New Enquiry from {data['name']}", body),
    })


def send_user_confirmation(name: str, email: str, subject: str = "") -> None:
    """
    Sends a branded confirmation email to the client.
    """
    first_name = name.strip().split()[0] if name.strip() else name

    body = f"""
    <h2 style="margin:0 0 8px;font-size:22px;font-weight:800;color:#0f1117;">We've Got Your Message, {first_name}.</h2>
    <p style="margin:0 0 24px;color:#666;font-size:15px;line-height:1.7;">
      Thank you for reaching out to <strong>UASE Tech Studio</strong>. We take every enquiry seriously &mdash;
      you can expect a personal response from Usty or our team within <strong>24 hours</strong> (usually sooner).
    </p>

    <!-- What to expect -->
    <div style="background:#f8f9fb;border:1px solid #eee;border-radius:12px;padding:24px;margin-bottom:24px;">
      <p style="margin:0 0 16px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#aaa;">What happens next</p>
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="padding:8px 0;vertical-align:top;">
            <span style="display:inline-block;background:{BRAND_COLOR};color:#000;width:24px;height:24px;border-radius:50%;text-align:center;line-height:24px;font-size:11px;font-weight:800;margin-right:12px;">1</span>
            <span style="font-size:14px;color:#333;">We review your message and project requirements</span>
          </td>
        </tr>
        <tr>
          <td style="padding:8px 0;vertical-align:top;">
            <span style="display:inline-block;background:{BRAND_COLOR};color:#000;width:24px;height:24px;border-radius:50%;text-align:center;line-height:24px;font-size:11px;font-weight:800;margin-right:12px;">2</span>
            <span style="font-size:14px;color:#333;">Usty reaches out to discuss your goals in detail</span>
          </td>
        </tr>
        <tr>
          <td style="padding:8px 0;vertical-align:top;">
            <span style="display:inline-block;background:{BRAND_COLOR};color:#000;width:24px;height:24px;border-radius:50%;text-align:center;line-height:24px;font-size:11px;font-weight:800;margin-right:12px;">3</span>
            <span style="font-size:14px;color:#333;">We architect a solution and share a proposal</span>
          </td>
        </tr>
      </table>
    </div>

    <!-- Quick links -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
      <tr>
        <td width="50%" style="padding-right:6px;">
          <a href="https://uase.tech/portfolio/" style="display:block;text-align:center;background:#f8f9fb;border:1px solid #eee;border-radius:10px;padding:14px;text-decoration:none;color:#333;font-size:13px;font-weight:600;">
            &#128269; View Portfolio
          </a>
        </td>
        <td width="50%" style="padding-left:6px;">
          <a href="https://carstrims-app.vercel.app/" style="display:block;text-align:center;background:#f8f9fb;border:1px solid #eee;border-radius:10px;padding:14px;text-decoration:none;color:#333;font-size:13px;font-weight:600;">
            &#9889; See CARSTRIMS Live
          </a>
        </td>
      </tr>
    </table>

    <p style="margin:0;color:#888;font-size:13px;line-height:1.7;">
      In the meantime, feel free to WhatsApp us directly at
      <a href="https://wa.me/2349133549399" style="color:{BRAND_COLOR};font-weight:600;">+234 913 354 9399</a> for urgent enquiries.
    </p>
    """
    resend.Emails.send({
        "from": "UASE Tech Studio <onboarding@resend.dev>",
        "to": [email],
        "reply_to": "uasetechstudio@gmail.com",
        "subject": "We received your message — UASE Tech Studio",
        "html": _base_html(f"Message received, {first_name}!", body),
    })


def send_admin_reply(to_email: str, name: str, message: str) -> None:
    """
    Sends a direct reply from admin to a client (used from Django admin).
    """
    first_name = name.strip().split()[0] if name.strip() else name

    body = f"""
    <h2 style="margin:0 0 8px;font-size:22px;font-weight:800;color:#0f1117;">Hello {first_name},</h2>
    <p style="margin:0 0 24px;color:#666;font-size:14px;">A response from UASE Tech Studio:</p>

    <div style="background:#f8f9fb;border:1px solid #eee;border-left:3px solid {BRAND_COLOR};border-radius:10px;padding:20px 24px;margin-bottom:28px;">
      <p style="margin:0;font-size:15px;color:#333;line-height:1.75;white-space:pre-wrap;">{message}</p>
    </div>

    <p style="margin:0;color:#888;font-size:13px;">
      Reply directly to this email or reach us on WhatsApp:
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
