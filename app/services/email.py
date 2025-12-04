from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Optional
from app.core.config import Config
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails via SendGrid"""
    
    def __init__(self):
        self.api_key = Config.get_sendgrid_api_key()
        self.from_email = Config.get_sendgrid_from_email()
        self._is_configured = bool(self.api_key)
        
        # Debug logging
        if self.api_key:
            print(f"SendGrid API key found: {self.api_key[:10]}...{self.api_key[-10:]}")
        else:
            print("SendGrid API key NOT found in environment")
        
        print(f"SendGrid from email: {self.from_email}")
        
        if self._is_configured:
            self.client = SendGridAPIClient(api_key=self.api_key)
            print("SendGrid client initialized successfully")
        else:
            self.client = None
            warning_msg = "SendGrid API key not configured. Email notifications will be disabled."
            logger.warning(warning_msg)
            print(warning_msg)
    
    def send_contact_notification(
        self,
        to_email: str,
        name: str,
        email: str,
        message: str,
        subject: Optional[str] = None
    ) -> bool:
        """Send email notification for contact form submission"""
        if not self._is_configured:
            error_msg = "SendGrid not configured. Skipping email notification."
            logger.warning(error_msg)
            print(error_msg)  # Also print for visibility
            return False
        
        try:
            # Create email content
            email_subject = f"New Contact Form Submission: {subject}" if subject else "New Contact Form Submission"
            
            email_body = f"""
A new contact form submission has been received:

Name: {name}
Email: {email}
Subject: {subject if subject else '(No subject)'}

Message:
{message}

---
This is an automated notification from FieldPal.ai contact form.
"""
            
            html_body = f"""
<html>
<body>
<h2>New Contact Form Submission</h2>
<p><strong>Name:</strong> {name}</p>
<p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
<p><strong>Subject:</strong> {subject if subject else '(No subject)'}</p>
<hr>
<p><strong>Message:</strong></p>
<p style="white-space: pre-wrap;">{message}</p>
<hr>
<p><em>This is an automated notification from FieldPal.ai contact form.</em></p>
</body>
</html>
"""
            
            mail_message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=email_subject,
                plain_text_content=email_body,
                html_content=html_body
            )
            
            print(f"Attempting to send email to {to_email} from {self.from_email}")
            response = self.client.send(mail_message)
            
            # SendGrid send() returns a Response object with status_code
            # Success is typically 202 Accepted
            print(f"SendGrid response status: {response.status_code}")
            if hasattr(response, 'headers'):
                print(f"SendGrid response headers: {dict(response.headers)}")
            if hasattr(response, 'body'):
                print(f"SendGrid response body: {response.body}")
            
            # SendGrid returns 202 for accepted emails
            if response.status_code in [200, 202]:
                success_msg = f"Contact notification email sent successfully to {to_email}"
                logger.info(success_msg)
                print(success_msg)
                return True
            else:
                error_msg = f"Failed to send email. Status code: {response.status_code}"
                if hasattr(response, 'body'):
                    error_msg += f", Body: {response.body}"
                logger.error(error_msg)
                print(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Error sending contact notification email: {e}"
            logger.error(error_msg, exc_info=True)
            print(error_msg)
            import traceback
            traceback.print_exc()
            return False

# Singleton instance
_email_service = None

def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


