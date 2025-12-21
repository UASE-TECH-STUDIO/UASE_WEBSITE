import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY


def send_admin_notification(data):
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


def send_user_confirmation(name, email):
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
