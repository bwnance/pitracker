import smtplib
import ssl

import os


class SMTPServer:
    server = None

    def __init__(self):
        self.SMTP_HOST = os.getenv("SMTP_HOST")
        self.SMTP_PORT = os.getenv("SMTP_PORT")
        self.SMTP_LOGIN = os.getenv("SMTP_LOGIN")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        self.SENDER_EMAIL = os.getenv("SENDER_EMAIL")
        context = ssl.create_default_context()
        server = smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT)
        # breakpoint()
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(self.SMTP_LOGIN, self.SMTP_PASSWORD)
        self.server = server

    def send_email(self, emails, msg):
        self.server.sendmail(self.SENDER_EMAIL, emails, msg)
