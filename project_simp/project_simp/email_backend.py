# project_platform/email_backend.py
import ssl
from django.core.mail.backends.smtp import EmailBackend


class CustomEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False

        import smtplib
        self.connection = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
        self.connection.ehlo()

        if self.use_tls:
            # Create an SSL context that skips certificate verification
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            self.connection.starttls(context=context)
            self.connection.ehlo()

        if self.username and self.password:
            self.connection.login(self.username, self.password)

        self.num_sent_messages = 0
        return True