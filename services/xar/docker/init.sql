create extension pg_cron;

create table projects (
    id     uuid primary key default gen_random_uuid(),
    ts     timestamptz default now(),
    name   varchar(128) not null unique,
    active boolean default true
);

create table data (
    project_id uuid not null references projects,
    ts  timestamptz default now(),
    k   varchar(32) not null,
    v   varchar(128) not null,
    unique (project_id, k)
);

create table archived_data (
    project_id uuid not null references projects,
    ts  timestamptz default now(),
    k   varchar(32) not null,
    v   varchar(128) not null,
    unique (project_id, k)
) partition by list(project_id);

create or replace function archive() returns void as $$
declare
  p record;
begin
  for p in
    select project_id, (select name from projects where id = project_id) as name
    from data
    group by project_id
    having max(ts) < now() - interval '5 minutes'
  loop
    begin
        execute format('create table data_%s partition of archived_data for values in (%L);', p.name, p.project_id);
    exception when others then
    end;
    begin
        update projects set active = false where id = p.project_id;
        with d as (
            delete from data
            where project_id = p.project_id
            returning *
        )
        insert into archived_data
        select * from d;
    exception when others then
    end;
  end loop;

  return;
end
$$ language plpgsql;

select cron.schedule('* * * * *', $$ select archive(); $$);
