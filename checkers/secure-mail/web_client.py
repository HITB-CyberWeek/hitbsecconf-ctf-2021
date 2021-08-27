#!/usr/bin/env python3

import asyncio
import websockets
import json
import re
from checker_helper import *
from dataclasses import dataclass

PORT = 8080
TIMEOUT = 5

@dataclass
class EmailItem:
    index: int

class WebClient:
    def __init__(self, host):
        self.uri = "ws://%s:%i" % (host, PORT)

    async def __aenter__(self):
        trace("Connecting to %s" % self.uri)
        try:
            self.ws = await asyncio.wait_for(websockets.connect(self.uri), TIMEOUT)
        except asyncio.exceptions.TimeoutError:
            verdict(DOWN, 'Web connection error: timeout', "Web connection error: timeout")
        except (ConnectionRefusedError, OSError) as e:
            verdict(DOWN, 'Web connection error: connection refused', "Web connection error: %s" % str(e))
        except websockets.exceptions.InvalidStatusCode as e:
            verdict(DOWN, 'Web connection error', "Web connection error: %s" % str(e))
        return self

    async def __aexit__(self, *args):
        await self.ws.close()

    async def execute_command(self, command, have_result=True):
        trace("Executing '%s' command" % command)
        try:
            await asyncio.wait_for(self.ws.send(command), TIMEOUT)
        except asyncio.exceptions.TimeoutError:
            verdict(DOWN, 'Web protocol error: timeout', "Web protocol error (timeout): can't execute '%s' command" % command)
        except (ConnectionRefusedError, OSError) as e:
            verdict(DOWN, 'Web connection error: connection refused', "Web connection error: %s" % str(e))

        if have_result:
            trace("Reading command result")
            try:
                result = await asyncio.wait_for(self.ws.recv(), TIMEOUT)
            except asyncio.exceptions.TimeoutError:
                verdict(DOWN, 'Web protocol error: timeout', "Web protocol error (timeout): can't receive command result")
            except (ConnectionRefusedError, OSError) as e:
                verdict(DOWN, 'Web connection error: connection refused', "Web connection error: %s" % str(e))
            trace("Command result: %s" % str(result))

            try:
                result_json = json.loads(result)
            except json.decoder.JSONDecodeError as e:
                verdict(MUMBLE, 'Web protocol error: invalid data', "Web protocol error: command returned bad json, error: %s" % str(e))

            if not 'exit_code' in result_json:
                verdict(MUMBLE, 'Web protocol error: bad data', "Web protocol error: command result does not contain 'exit_code'")

            if result_json['exit_code']:
                verdict(MUMBLE, 'Web protocol error: command error', "Web protocol error: command return non-zero exit code %s" % result_json['exit_code'])

            if not 'output' in result_json:
                verdict(MUMBLE, 'Web protocol error: bad data', "Web protocol error: command result does not contain 'output'")

            return result_json

    async def create_user(self, user, password):
        await self.execute_command('80', have_result=False)
        await self.execute_command("adduser %s %s" % (user, password))

    async def login(self, user, password):
        await self.execute_command('80', have_result=False)
        await self.execute_command("login %s %s" % (user, password))

    async def list_emails(self):
        ls_result = await self.execute_command('ls')

        result = list()
        for l in ls_result['output'].splitlines():
            m = re.match(r"^(?P<name>\d+)\/", l)
            if not m:
                verdict(MUMBLE, 'Web protocol error: bad data', "Web protocol error: 'ls' command result has invalid format")
            result.append(EmailItem(int(m.group('name'))))
        return result

    async def list_attachments(self):
        ls_result = await self.execute_command('ls')
        return ls_result['output'].splitlines()

    async def cd(self, dir):
        cd_result = await self.execute_command("cd %s" % dir)
        if not 'working_dir' in cd_result:
            verdict(MUMBLE, 'Web protocol error: bad data', "Web protocol error: command result does not contain 'working_dir'")

        if (dir == 'attachments' and not cd_result['working_dir'].endswith('attachments')) or (isinstance(dir, int) and cd_result['working_dir'] != '/%i' % dir):
            verdict(MUMBLE, 'Web protocol error: bad data', "Web protocol error: command result contains unexpected 'working_dir'")

    async def list_email_items(self):
        ls_result = await self.execute_command('ls')

        result = ls_result['output'].splitlines()
        if len(set(result) - set(['attachments/', 'html', 'text'])):
            verdict(MUMBLE, 'Web protocol error: bad data', "Web protocol error: 'ls' command result contains unexpected items")

        return result

    async def cat(self, file):
        cat_result = await self.execute_command('cat %s' % file)
        return cat_result['output']
