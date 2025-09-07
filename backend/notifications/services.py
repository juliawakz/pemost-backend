import logging

from decouple import config
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Mail

logger = logging.getLogger(__file__)


class MessagingService:
    @staticmethod
    def send_email(to, from_email, subject, msg=None, html_content=None):
        """
        Sends an email with plain text and/or HTML content using SendGrid.

        :param to: Recipient email (str or list of str)
        :param from_email: Sender email (str)
        :param subject: Email subject (str)
        :param msg: Plain text message (str, optional)
        :param html_content: HTML message (str, optional)
        """
        if not msg and not html_content:
            logger.warning("No message content provided for email")
            return

        # Create Mail object
        message = Mail(
            from_email=from_email,
            to_emails=to,
            subject=subject,
        )

        # Prefer plain text as fallback if both exist
        if msg:
            message.add_content(Content("text/plain", msg))

        if html_content:
            message.add_content(Content("text/html", html_content))

        try:
            sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
            response = sg.send(message)
            logger.info("Email sent to %s, status: %s", to, response.status_code)
            return response
        except Exception as e:
            logger.error("Error sending email: %s", e, exc_info=True)
            return None
