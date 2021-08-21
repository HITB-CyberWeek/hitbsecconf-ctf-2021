FROM postgres:13

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y postgresql-13-cron && apt-get clean
