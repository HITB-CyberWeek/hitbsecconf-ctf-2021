FROM debian:buster-slim

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y -qq \
        clamav-daemon \
        netcat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/clamav && \
    chown clamav:clamav /var/run/clamav && \
    chmod 750 /var/run/clamav

ADD ./clamd.conf /etc/clamav/clamd.conf
ADD ./db.hdb /var/lib/clamav/db.hdb

EXPOSE 3310

CMD ["clamd"]
