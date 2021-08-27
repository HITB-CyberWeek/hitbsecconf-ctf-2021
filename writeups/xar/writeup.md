# XAR

## Description

XAR service is a simple http service written in typescript. It allows clients to create projects and store/fetch data like a key-value storage. Old projects are archived after 5 minutes of inactivity and data from those projects is moved to archive. This archive is a special partition table which is partitioned by cron task in postgresql.


## Flags

Flags are stored in table `data`.

## Vuln

In `archive` function service detects old projects and creates new partitions for them. Partition's name is `data_$project.name`:

`execute format('create table data_%s partition of archived_data for values in (%L);', p.name, p.project_id);`

There is an SQL injection in this query. Attacker can create a project with arbitrary SQL code in it's name which will be executed while archiving. For example `"_();insert into archived_data select'{project_id}',now(),row_number()over(),v from data;--"`.

You can find full exploit code here: https://github.com/HITB-CyberWeek/hitbsecconf-ctf-2021/blob/main/sploits/xar/sploit.py.
