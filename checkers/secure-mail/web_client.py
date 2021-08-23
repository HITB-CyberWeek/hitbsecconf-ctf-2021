#!/usr/bin/env python3

import asyncio
#import concurrent.futures
import websockets
from checker_helper import *

PORT = 8080
TIMEOUT = 5

class WebClient:
    def __init__(self, host):
        self.uri = "ws://%s:%i" % (host, PORT)

    async def __aenter__(self):
        trace("Connecting to %s" % self.uri)
        try:
            self.ws = await asyncio.wait_for(websockets.connect(self.uri), TIMEOUT)
        except asyncio.exceptions.TimeoutError:
            verdict(DOWN, 'Web connection error', "Web connection error: timeout")
        except ConnectionRefusedError as e:
            verdict(DOWN, 'Web connection error', "Web connection error: %s" % str(e))
        return self

    async def __aexit__(self, *args):
        await self.ws.close()

    async def create_user(self, user, password):
        trace("Setting term_size=80")
        try:
            await asyncio.wait_for(self.ws.send('80'), TIMEOUT)
        except asyncio.exceptions.TimeoutError:
            verdict(DOWN, 'Web protocol error', "Web protocol error: can't send term size")

        cmd = "adduser %s %s" % (user, password)
        trace("Executing '%s' command" % cmd)
        try:
            await asyncio.wait_for(self.ws.send("adduser %s %s" % (user, password)), TIMEOUT)
        except asyncio.exceptions.TimeoutError:
            verdict(DOWN, 'Web protocol error', "Web protocol error: can't send adduser command")

        try:
            result = await asyncio.wait_for(self.ws.recv(), TIMEOUT)
        except asyncio.exceptions.TimeoutError:
            verdict(DOWN, 'Web protocol error', "Web protocol error: can't receive command result")
        trace("Command result: %s" % str(result))
