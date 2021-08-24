#!/usr/bin/python3
# Developed by Alexander Bersenev from Hackerdom team, bay@hackerdom.ru

"""Takes a snapshot of vm"""

import sys
import time
import os
import traceback
import re

import do_api
from cloud_common import (log_progress, call_unitl_zero_exit, #get_cloud_ip,
                          SSH_OPTS #SSH_YA_OPTS
                          )

TEAM = int(sys.argv[1])
NAME = sys.argv[2]

IMAGE_VM_NAME = "team%d" % TEAM

def log_stderr(*params):
    print("Team %d:" % TEAM, *params, file=sys.stderr)


def main():
    if not re.fullmatch(r"[0-9a-zA-Z_]{,64}", NAME):
        print("msg: ERR, name validation error")
        return 1

    image_state = open("db/team%d/image_deploy_state" % TEAM).read().strip()

    if image_state == "NOT_STARTED":
        print("msg: ERR, vm is not started")
        return 1

    if image_state == "RUNNING":
        ids = do_api.get_ids_by_vmname(IMAGE_VM_NAME)
        if not ids:
            log_stderr("failed to find vm")
            return 1

        if len(ids) > 1:
            log_stderr("more than one vm with this name exists")
            return 1

        result = do_api.take_vm_snapshot(list(ids)[0], IMAGE_VM_NAME + "-" + NAME)
        if not result:
            log_stderr("take shapshot failed")
            return 1

        print("msg: OK, snapshoting is in progress, it takes several minutes")
    return 0

if __name__ == "__main__":
    sys.stdout = os.fdopen(1, 'w', 1)
    print("started: %d" % time.time())
    exitcode = 1
    try:
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        exitcode = main()
    except:
        traceback.print_exc()
    print("exit_code: %d" % exitcode)
    print("finished: %d" % time.time())
