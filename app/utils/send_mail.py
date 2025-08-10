from flask import current_app
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
# local
from app.models import ContactMessage
from ..extensions import mail


def send_contact_email(contact:ContactMessage):
    """
    Send contact form email to admin
    Args:
        contact: ContactMessage model instance
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create message
        msg = Message(
            subject=f"New Contact Form: {contact.subject}",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[current_app.config['ADMIN_EMAIL']],  # Get from config
            body=f"""
                    New contact form submission:

                    From: {contact.name}
                    Email: {contact.email}
                    Subject: {contact.subject}

                    Message:
                    {contact.message}

                    Sent at: {contact.created_at}
                                """.strip()
                            )
        # Send email
        mail.send(msg)
        current_app.logger.info(f"Contact form email sent successfully for {contact.email}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send contact form email: {e}")
        return False
    
# TO DO:
def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=current_app.config["MAIL_USERNAME"],
    )
    mail.send(msg)

# TO DO:
def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=current_app.config["SECURITY_PASSWORD_SALT"])

# TO DO:
def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(
            token, salt=current_app.config["SECURITY_PASSWORD_SALT"], max_age=expiration
        )
        return email
    except Exception:
        return False