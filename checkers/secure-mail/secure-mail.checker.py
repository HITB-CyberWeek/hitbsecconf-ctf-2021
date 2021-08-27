#!/usr/bin/env python3
  
import sys
import uuid
import traceback
import asyncio
import json
import base64
import binascii
import time
import requests
from smtp_client import SmtpClient
from web_client import WebClient
from user_db import UserDb
from link_generator import LinkGenerator
from checker_helper import *

SMTP_PORT = 2525

def info():
    verdict(OK, "vulns: 1")

async def check(args):
    if len(args) != 1:
        verdict(CHECKER_ERROR, "Wrong args count", "Wrong args count for check()")
    host = args[0]
    trace("check(%s)" % host)

    db = UserDb()
    smtp_client = SmtpClient(host)
    user_id = str(uuid.uuid4())

    user = db.create_user(host, user_id)
    async with WebClient(host) as wc:
        await wc.create_user(user.name, user.password)

    try:
        link, name = LinkGenerator().get_random_link()
        smtp_client.send_phishing_message(to=user.name, link=link)
        time.sleep(3)

        r = requests.get(f"http://10.60.56.129/check?file={name}")
        if not r.json()[0]:
            verdict(MUMBLE, "File download error", "File download error")
    except Exception as e:
        trace(f"Request failed: {str(e)}")

    verdict(OK)

async def put(args):
    if len(args) != 4:
        verdict(CHECKER_ERROR, "Wrong args count", "Wrong args count for put()")
    host, flag_id, flag_data, vuln = args
    trace("put(%s, %s, %s, %s)" % (host, flag_id, flag_data, vuln))

    smtp_client = SmtpClient(host)
    db = UserDb()

    user = db.create_user(host, flag_id)
    async with WebClient(host) as wc:
        await wc.create_user(user.name, user.password)
    smtp_client.send_secret_message(to=user.name, secret=flag_data)

    flag_id = base64.b64encode(json.dumps([user.name, user.password]).encode()).decode()
    verdict(OK, flag_id)

async def get(args):
    if len(args) != 4:
        verdict(CHECKER_ERROR, "Wrong args count", "Wrong args count for get()")
    host, flag_id, flag_data, vuln = args
    trace("get(%s, %s, %s, %s)" % (host, flag_id, flag_data, vuln))

    db = UserDb()
    user = db.read_user(host, flag_id)

    async with WebClient(host) as wc:
        await wc.login(user.name, user.password)

        emails = await wc.list_emails()
        if len(emails) != 1:
            verdict(CORRUPT, "Can't find email", "Got %i emails, expected 1" % len(emails))
        if emails[0].index != 0:
            verdict(MUMBLE, "Web protocol error: bad data", "Email has unexpected name: %i" % emails[0].index)

        await wc.cd(emails[0].index)

        email_items = await wc.list_email_items()
        if not 'text' in email_items:
            verdict(MUMBLE, "Web protocol error: bad data", "Email does not contain 'text' part")

        trace("Reading text part of email")
        content = await wc.cat('text')
        if content == 'See attachments':
            if not 'attachments/' in email_items:
                verdict(CORRUPT, "Unexpected email", "Email does not contain attachments part")

            trace("Reading attachment part of email")
            await wc.cd('attachments')
            attachments = await wc.list_attachments()
            if len(attachments) != 1:
                verdict(CORRUPT, "Unexpected email", "Email contains unexpected number of attachments: %i" % len(attachments))

            if attachments[0] != 'secret':
                verdict(CORRUPT, "Unexpected email", "Email contains unexpected attachment name: %s" % attachments[0])

            content = await wc.cat('secret')
            try:
                decoded_content = base64.b64decode(content).decode('utf-8')
            except binascii.Error as e:
                verdict(MUMBLE, "Web protocol error: bad data", "Attachment has invalid base64 encoding: %s" % str(e))
            if str(decoded_content) != flag_data:
                verdict(CORRUPT, "Unexpected email", "Email contains unexpected data")
            else:
                verdict(OK)

        elif content == 'See HTML part':
            trace("Reading html part of email")
            content = await wc.cat('html')

        content_lines = content.splitlines()
        if len(content_lines) != 3:
            verdict(CORRUPT, "Unexpected email", "Email contains unexpected number of lines")

        if content_lines[1] != "I have a confidential message for you: %s" % flag_data:
            verdict(CORRUPT, "Unexpected email", "Email contains unexpected data")

    verdict(OK)

def main(args):
    if len(args) == 0:
        verdict(CHECKER_ERROR, "No args")
    try:
        if args[0] == "info":
            info()
        elif args[0] == "check":
            asyncio.get_event_loop().run_until_complete(check(args[1:]))
        elif args[0] == "put":
            asyncio.get_event_loop().run_until_complete(put(args[1:]))
        elif args[0] == "get":
            asyncio.get_event_loop().run_until_complete(get(args[1:]))
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
