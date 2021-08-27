#!/usr/bin/env python3

import json
import logging
import pathlib
import random
import string
import time
from typing import Tuple

import requests.auth

import checklib
import checklib.http
import checklib.random
from proof_of_work import challenge_responses


class SandboxChecker(checklib.http.HttpJsonChecker):
    port = 8000

    def info(self):
        print('vulns: 1')
        self.exit(checklib.StatusCode.OK)

    def check(self, address: str):
        self._check_main_page()

    def put(self, address: str, flag_id: str, flag: str, _vuln: str):
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

    def get(self, address: str, flag_id: str, flag: str, _vuln: str):
        data = json.loads(flag_id)
        username = data["username"]
        password = data["password"]
        program_id = data["program_id"]

        self._login(username, password)
        challenge_id, challenge_prefix = self._get_proof_of_work_challenge(program_id)

        if challenge_prefix not in challenge_responses:
            self.exit(checklib.StatusCode.MUMBLE, "Unknown proof-of-work challenge, can't solve it")

        challenge_response = challenge_responses[challenge_prefix]

        one_time_notepad_data = [random.randint(0, 255) for _ in range(len(flag))]
        one_time_notepad = " ".join(map(str, one_time_notepad_data))
        start_time = time.monotonic()
        output = self._run_program(program_id, one_time_notepad, challenge_id, challenge_response)
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

    def _register_user(self, username: str, password: str) -> int:
        logging.info('Try to register a user %r with password %r' % (username, password))
        r = self.try_http_post("/users", json={
            "username": username,
            "password": password,
        })

        user_id = int(r['user']['id'])
        logging.info('Success. User id is %d' % (user_id, ))
        return user_id

    def _login(self, username: str, password: str):
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

    def _upload_program(self, program_code: str) -> int:
        logging.info('Try to upload a program')
        r = self.try_http_post("/programs", json={
            "code": program_code,
        })

        self.mumble_if_false("program" in r and isinstance(r["program"], dict), "Can't find 'program' key in response for POST /programs")
        self.mumble_if_false("id" in r["program"], "Can't find 'program' key in response for /programs")
        program_id = int(r["program"]["id"])

        logging.info("Success. Program id is %d" % (program_id, ))
        return program_id

    def _run_program(self, program_id: int, stdin: str, challenge_id: int, challenge_response: str) -> str:
        logging.info('Try to run a program %d with stdin %r' % (program_id, stdin))
        r = self.try_http_post("/programs/%d/run" % (program_id, ), json={
            "input": stdin,
            "challenge_id": challenge_id,
            "challenge_response": challenge_response,
        })

        self.mumble_if_false("log" in r, "Can't find 'log' key in response for POST /programs/?/runs")
        self.mumble_if_false("output" in r, "Can't find 'output' key in response for POST /programs/?/runs")

        return r["output"]

    def _get_proof_of_work_challenge(self, program_id: int) -> Tuple[int, str]:
        r = self.try_http_post("/programs/%d/challenge" % (program_id, ))
        self.mumble_if_false("challenge_id" in r, "Can't find `challenge_id` key in response for POST /programs/?/challenge")
        self.mumble_if_false("prefix" in r, "Can't find `prefix` key in response for POST /programs/?/challenge")
        return r["challenge_id"], r["prefix"]


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = "Bearer " + self.token
        return r


if __name__ == '__main__':
    SandboxChecker().run()
