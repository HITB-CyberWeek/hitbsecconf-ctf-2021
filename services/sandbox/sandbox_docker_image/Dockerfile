FROM alpine:3.14.0

RUN set -ex && apk add --no-cache gcc musl-dev

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
