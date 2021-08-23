#!/usr/bin/env python3
  
import sys
import traceback
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid
import asyncio
import websockets
from smtp_client import SmtpClient
from web_client import WebClient
from user_db import UserDb
from checker_helper import *

SMTP_PORT = 2525

def info():
    verdict(OK, "vulns: 1")

def check(args):
    if len(args) != 1:
        verdict(CHECKER_ERROR, "Wrong args count", "Wrong args count for check()")
    host = args[0]
    trace("check(%s)" % host)

    msg = EmailMessage()
    msg["Subject"] = "Interesting business proposal"
    msg["From"] = Address("Elon Musk", "Elon.Musk", "tesla.com")
    msg["To"] = Address("Receiver", "receiver", "hackerdom.com")
    msg["Cc"] = Address("Receiver", "receiver1", "hackerdom.com")
    msg["Bcc"] = Address("Receiver", "user", "hackerdom.com")

    text = """\
Dear Sir/Madam,
I have an interesting business proposal I want to share with you.

---
Elon Musk"""

    html = """\
<html>
  <body>
    <p>Dear Sir/Madam,<br>
       I have an <a href="http://www.realpython.com">interesting business proposal</a> I want to share with you.<br><br>
       ---<br>
       Elon Musk
    </p>
  </body>
</html>
"""

    msg.set_content(text)
    msg.add_alternative(html, subtype='html')

    filename = 'qqq'

    with open('/etc/passwd', 'rb') as fp:
        msg.add_attachment(fp.read(), maintype='application', subtype='octet-stream', filename=filename)

    with smtplib.SMTP(host, SMTP_PORT) as s:
        s.send_message(msg)

    sys.exit(OK)

async def put(args):
    if len(args) != 4:
        verdict(CHECKER_ERROR, "Wrong args count", "Wrong args count for put()")
    host, flag_id, flag_data, vuln = args
    trace("put(%s, %s, %s, %s)" % (host, flag_id, flag_data, vuln))

    smtp_client = SmtpClient(host)

    with UserDb() as db:
        user = db.create_user(host, flag_id)
        async with WebClient(host) as wc:
            await wc.create_user(user.name, user.password)
        smtp_client.send_secret_message(to=user.name, secret=flag_data)

    verdict(OK)

def get(args):
    if len(args) != 4:
        verdict(CHECKER_ERROR, "Wrong args count", "Wrong args count for get()")
    host, flag_id, flag_data, vuln = args
    trace("get(%s, %s, %s, %s)" % (host, flag_id, flag_data, vuln))

    sys.exit(OK)

def main(args):
    if len(args) == 0:
        verdict(CHECKER_ERROR, "No args")
    try:
        if args[0] == "info":
            info()
        elif args[0] == "check":
            check(args[1:])
        elif args[0] == "put":
            asyncio.get_event_loop().run_until_complete(put(args[1:]))
        elif args[0] == "get":
            get(args[1:])
        else:
            verdict(CHECKER_ERROR, "Checker error", "Wrong action: " + args[0])
    except Exception as e:
        verdict(CHECKER_ERROR, "Checker error", "Exception: %s" % traceback.format_exc())

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
        verdict(CHECKER_ERROR, "Checker error (NV)", "No verdict")
    except Exception as e:
        verdict(CHECKER_ERROR, "Checker error (CE)", "Exception: %s" % e)
