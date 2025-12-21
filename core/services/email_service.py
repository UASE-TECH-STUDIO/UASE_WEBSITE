import resend
from django.conf import settings

# Initialize Resend with API key
resend.api_key = settings.RESEND_API_KEY


def send_admin_notification(data: dict) -> None:
    """
    Sends a notification email to admin when a new contact form is submitted.
    """
    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [settings.CONTACT_RECIPIENT_EMAIL],
        "subject": f"[UASE CONTACT] {data['subject']}",
        "html": f"""
            <h3>New Contact Message</h3>
            <p><strong>Name:</strong> {data['name']}</p>
            <p><strong>Email:</strong> {data['email']}</p>
            <p><strong>Country:</strong> {data['country']}</p>
            <p><strong>IP:</strong> {data['ip_address']}</p>
            <hr>
            <p>{data['message']}</p>
        """
    })


def send_user_confirmation(name: str, email: str) -> None:
    """
    Sends confirmation email to the user after contact submission.
    """
    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [email],
        "subject": "We received your message | UASE Tech Studio",
        "html": f"""
            <p>Hello {name},</p>
            <p>Thank you for contacting <strong>UASE Tech Studio</strong>.</p>
            <p>We have received your message and will respond shortly.</p>
            <br>
            <p>— UASE Tech Studio</p>
        """
    })


def send_admin_reply(to_email: str, name: str, message: str) -> None:
    """
    Sends an admin reply directly from Django admin.
    """
    resend.Emails.send({
        "from": "UASE TECH-STUDIO <noreply@uase.tech>",
        "to": [to_email],
        "subject": "Reply from UASE TECH-STUDIO",
        "html": f"""
            <p>Hello {name},</p>
            <p>{message}</p>
            <br>
            <p>
                Regards,<br>
                <strong>UASE TECH-STUDIO</strong><br>
                https://uase.tech
            </p>
        """
    })
