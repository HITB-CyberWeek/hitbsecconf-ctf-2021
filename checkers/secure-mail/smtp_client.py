#!/usr/bin/env python3

import socket
import uuid
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
from random import randint
from checker_helper import *

PORT = 2525
DOMAIN = 'ctf.hitb.org'
TIMEOUT = 5
HTML_TEMPLATE = '<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"/></head><body><p>Dear Sir/Madam,<br>I have a confidential message for you: %s<br>Keep it a secret!</p></body></html>'
TEXT_TEMPLATE = "Dear Sir/Madam,\nI have a confidential message for you: %s\nKeep it a secret!"

class SmtpClient:
    def __init__(self, host):
        self._host = host

    def send_secret_message(self, to, secret):
        msg = EmailMessage()
        msg["Subject"] = "Secret message"
        msg["From"] = Address(username=str(uuid.uuid4()), domain=DOMAIN)

        rnd = randint(0, 2)
        if rnd == 0:
            msg["To"] = Address(username=to, domain=DOMAIN)
            trace("'To' header will contain target username")
        else:
            msg["To"] = Address(username=str(uuid.uuid4()), domain=DOMAIN)
            if rnd == 1:
                msg["Cc"] = Address(username=to, domain=DOMAIN)
                trace("'Cc' header will contain target username")

                if randint(0, 1) == 0:
                    msg["Bcc"] = Address(username=str(uuid.uuid4()), domain=DOMAIN)
            else:
                msg["Bcc"] = Address(username=to, domain=DOMAIN)
                trace("'Bcc' header will contain target username")
                if randint(0, 1) == 0:
                    msg["Cc"] = Address(username=str(uuid.uuid4()), domain=DOMAIN)

        text = ''
        html = ''
        attachment_data = ''

        rnd = randint(0, 2)
        if rnd == 0:
            trace("Text part will contain a secret")
            text = TEXT_TEMPLATE % secret
            if randint(0, 1) == 0:
                trace("Adding random HTML part")
                html = HTML_TEMPLATE % 'See text part'
            if randint(0, 1) == 0:
                trace("Adding random attachments part")
                attachment_data = 'See text part'
        else:
            if rnd == 1:
                trace("HTML part will contain a secret")
                text = 'See HTML part'
                html = HTML_TEMPLATE % secret
                if randint(0, 1) == 0:
                    trace("Adding random attachments part")
                    attachment_data = 'See HTML part'
            else:
                trace("Attachments part will contain a secret")
                text = 'See attachments'
                if randint(0, 1) == 0:
                    trace("Adding random HTML part")
                    html = HTML_TEMPLATE % 'See attachments'
                attachment_data = secret

        msg.set_content(text)
        if html:
            msg.add_alternative(html, subtype='html')

        if attachment_data:
            msg.add_attachment(attachment_data.encode('utf-8'), maintype='application', subtype='octet-stream', filename='secret')

        try:
            trace("Connecting to %s:%i" % (self._host, PORT))
            with smtplib.SMTP(self._host, PORT, timeout=TIMEOUT) as s:
                trace("Sending email to %s@%s" % (to, DOMAIN))
                s.send_message(msg)
        except (socket.timeout, ConnectionRefusedError) as e:
            verdict(DOWN, "SMTP connection error", "SMTP connection error: %s" % str(e))
        except smtplib.SMTPException as e:
            verdict(MUMBLE, "SMTP error", "SMTP error: %s" % str(e))

    def send_phishing_message(self, to, link):
        msg = EmailMessage()
        msg["Subject"] = "Interesting business proposal"
        msg["From"] = Address(username=str(uuid.uuid4()), domain=DOMAIN)

        rnd = randint(0, 2)
        if rnd == 0:
            msg["To"] = Address(username=to, domain=DOMAIN)
            trace("'To' header will contain target username")
        else:
            msg["To"] = Address(username=str(uuid.uuid4()), domain=DOMAIN)
            if rnd == 1:
                msg["Cc"] = Address(username=to, domain=DOMAIN)
                trace("'Cc' header will contain target username")

                if randint(0, 1) == 0:
                    msg["Bcc"] = Address(username=str(uuid.uuid4()), domain=DOMAIN)
            else:
                msg["Bcc"] = Address(username=to, domain=DOMAIN)
                trace("'Bcc' header will contain target username")
                if randint(0, 1) == 0:
                    msg["Cc"] = Address(username=str(uuid.uuid4()), domain=DOMAIN)

        text = """\
Dear Sir/Madam,
I have an interesting business proposal I want to share with you.

---
Elon Musk"""

        html = """\
<html>
  <body>
    <p>Dear Sir/Madam,<br>
       I have an <a href="%s">interesting business proposal</a> I want to share with you.<br><br>
       ---<br>
       Elon Musk
    </p>
  </body>
</html>
"""

        msg.set_content(text)
        msg.add_alternative(html % link, subtype='html')

        try:
            trace("Connecting to %s:%i" % (self._host, PORT))
            with smtplib.SMTP(self._host, PORT, timeout=TIMEOUT) as s:
                trace("Sending email to %s@%s" % (to, DOMAIN))
                s.send_message(msg)
        except (socket.timeout, ConnectionRefusedError) as e:
            verdict(DOWN, "SMTP connection error", "SMTP connection error: %s" % str(e))
        except smtplib.SMTPException as e:
            verdict(MUMBLE, "SMTP error", "SMTP error: %s" % str(e))
