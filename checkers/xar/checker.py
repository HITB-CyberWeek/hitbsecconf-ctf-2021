#!/usr/bin/env python3

import requests
import time
import traceback
import random
import string
import sys

from gornilo import CheckRequest, Verdict, Checker, PutRequest, GetRequest


checker = Checker()

PROJECTS_URL = "http://{host}:3000/projects"
PROJECT_URL = "http://{host}:3000/projects/{project_id}"
DATA_URL = "http://{host}:3000/projects/{project_id}/{key}"

ALPHA = string.ascii_letters + string.digits


def gen_string():
    return ''.join(random.choice(ALPHA) for _ in range(20))


class NetworkChecker:
    def __init__(self):
        self.verdict = Verdict.OK()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type in {requests.exceptions.ConnectionError, ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError}:
            self.verdict = Verdict.DOWN("Service is down")
        if exc_type in {requests.exceptions.HTTPError}:
            self.verdict = Verdict.MUMBLE("Incorrect http code")
        if exc_type in {TypeError}:
            self.verdict = Verdict.MUMBLE("Incorrect response schema")

        if exc_type:
            print(exc_type)
            print(exc_value.__dict__)
            traceback.print_tb(exc_traceback, file=sys.stdout)
        return True


@checker.define_check
def check_service(request: CheckRequest) -> Verdict:
    return Verdict.OK()


@checker.define_put(vuln_num=1, vuln_rate=1)
def put_flag(request: PutRequest) -> Verdict:
    with NetworkChecker() as nc:
        project_name, key = gen_string(), gen_string()

        r = requests.post(url=PROJECTS_URL.format(
            host=request.hostname), json={"name": project_name})
        r.raise_for_status()
        project_id = r.json()
        if not type(project_id) is str:
            return Verdict.MUMBLE("Incorrect response schema")

        r = requests.post(url=PROJECT_URL.format(
            host=request.hostname, project_id=project_id), json={"k": key, "v": request.flag})
        r.raise_for_status()

        t = str(int(time.time()))
        flag_id = f"{project_id}:{key}:{t}"
        nc.verdict = Verdict.OK(flag_id)
    return nc.verdict


@checker.define_get(vuln_num=1)
def get_flag(request: GetRequest) -> Verdict:
    with NetworkChecker() as nc:
        project_id, key, t = request.flag_id.strip().split(":")
        old_flag = int(time.time()) - int(t) > 7 * 60

        r = requests.get(url=PROJECT_URL.format(
            host=request.hostname, project_id=project_id))
        r.raise_for_status()
        project = r.json()
        if old_flag and project["active"]:
            return Verdict.MUMBLE("Projects are not being archived")

        r = requests.get(url=DATA_URL.format(
            host=request.hostname, project_id=project_id, key=key))
        r.raise_for_status()
        real_flag = r.json()
        if not type(real_flag) is str:
            return Verdict.MUMBLE("Incorrect response schema")

        if request.flag != real_flag:
            print(
                f"Different flags, expected: {request.flag}, real: {real_flag}")
            return Verdict.CORRUPT("Corrupt flag")
        nc.verdict = Verdict.OK()
    return nc.verdict


if __name__ == '__main__':
    checker.run()
