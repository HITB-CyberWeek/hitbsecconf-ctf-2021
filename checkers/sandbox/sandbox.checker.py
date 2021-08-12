#!/usr/bin/env python3

import json
import logging
import pathlib
import random
import string
import time

import requests.auth

import checklib
import checklib.http
import checklib.random


class SandboxChecker(checklib.http.HttpJsonChecker):
    port = 8000

    def info(self):
        print('vulns: 1')
        self.exit(checklib.StatusCode.OK)

    def check(self, address):
        self._check_main_page()

    def put(self, address, flag_id, flag, vuln):
        username = checklib.random.string(string.ascii_lowercase, 10)
        password = checklib.random.string(string.ascii_lowercase, 10)
        self._register_user(username, password)
        self._login(username, password)

        program = self._generate_program_code(flag)
        program_id = self._upload_program(program)

        # Print flag_id for calling get() after some time
        print(json.dumps({
            "username": username,
            "password": password,
            "program_id": program_id,
        }))

    def get(self, address, flag_id, flag, vuln):
        data = json.loads(flag_id)
        username = data["username"]
        password = data["password"]
        program_id = data["program_id"]

        self._login(username, password)

        one_time_notepad_data = [random.randint(0, 255) for _ in range(len(flag))]
        one_time_notepad = " ".join(map(str, one_time_notepad_data))
        start_time = time.monotonic()
        output = self._run_program(program_id, one_time_notepad)
        logging.info("Program finished at %f seconds" % (time.monotonic() - start_time))

        output_data = list(map(int, output.split()))
        restored_data = [one_time_notepad_data[i] ^ output_data[i] for i in range(min(len(one_time_notepad_data), len(output_data)))]
        self.corrupt_if_false("".join(map(chr, restored_data)) == flag, "Program didn't write a flag to the output")

    def check_json_response(self, response: dict, url: str):
        """ Additional check for every JSON response """
        self.mumble_if_false(
            response.get("status") == 'ok',
            'Bad response from %s: status = %r' % (url, response.get("status"))
        )

    # INTERNAL METHODS:

    def _check_main_page(self):
        response = self.try_http_get(self.main_url)
        self.mumble_if_false(
            "Welcome to the Sandbox API" in response.get("welcome", ""),
            "Invalid content on %s" % (self.main_url, ),
            "Not found 'Welcome to the Sandbox API'"
        )

    def _register_user(self, username, password):
        logging.info('Try to register a user %r with password %r' % (username, password))
        r = self.try_http_post("/users", json={
            "username": username,
            "password": password,
        })

        user_id = int(r['user']['id'])
        logging.info('Success. User id is %d' % (user_id, ))
        return user_id

    def _login(self, username, password):
        logging.info('Try to login as "%s" with password "%s"' % (username, password))
        r = self.try_http_post("/login", data={
            "username": username,
            "password": password,
        })

        self.mumble_if_false("access_token" in r, "Can't authenticate as existing user")
        access_token = r.get("access_token", None)
        self._session.auth = BearerAuth(access_token)

    def _generate_program_code(self, flag: str) -> str:
        template = (pathlib.Path(__file__).parent / "template.c").read_text()
        return template.replace("%FLAG%", flag)

    def _upload_program(self, program_code):
        logging.info('Try to upload a program')
        r = self.try_http_post("/programs", json={
            "code": program_code,
        })

        self.mumble_if_false("program" in r and isinstance(r["program"], dict), "Can't find 'program' key in response for POST /programs")
        self.mumble_if_false("id" in r["program"], "Can't find 'program' key in response for /programs")
        program_id = int(r["program"]["id"])

        logging.info("Success. Program id is %d" % (program_id, ))
        return program_id

    def _run_program(self, program_id: int, stdin: str):
        logging.info('Try to run a program %d with stdin %r' % (program_id, stdin))
        r = self.try_http_post("/programs/%d/run" % (program_id, ), json={
            "input": stdin,
        })

        self.mumble_if_false("log" in r, "Can't find 'log' key in response for POST /programs/?/runs")
        self.mumble_if_false("output" in r, "Can't find 'output' key in response for POST /programs/?/runs")

        return r["output"]


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = "Bearer " + self.token
        return r


if __name__ == '__main__':
    SandboxChecker().run()
