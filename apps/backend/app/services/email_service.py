import logging
import aiosmtplib
from email.message import EmailMessage
from typing import List, Optional, Union
from app.models.user import User

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    async def send_email(
        user: User,
        subject: str,
        body: str,
        to_emails: Union[str, List[str]],
        is_html: bool = False
    ) -> bool:
        """
        Send an email using the user's SMTP credentials.
        """
        if not user.smtp_email or not user.smtp_password:
            logger.warning(f"User {user.email} does not have SMTP credentials configured.")
            return False

        if not user.smtp_server or not user.smtp_port:
             logger.warning(f"User {user.email} has incomplete SMTP configuration.")
             return False

        msg = EmailMessage()
        msg["From"] = user.smtp_email
        
        if isinstance(to_emails, str):
            to_emails = [to_emails]
            
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject
        
        if is_html:
            msg.set_content(body, subtype="html")
        else:
            msg.set_content(body)

        try:
            logger.info(f"Connecting to SMTP {user.smtp_server}:{user.smtp_port} for user {user.email}...")
            
            await aiosmtplib.send(
                msg,
                hostname=user.smtp_server,
                port=user.smtp_port,
                username=user.smtp_email,
                password=user.smtp_password,
                use_tls=True if user.smtp_port == 465 else False,
                start_tls=True if user.smtp_port == 587 else False,
            )
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email for user {user.email}: {e}")
            return False
