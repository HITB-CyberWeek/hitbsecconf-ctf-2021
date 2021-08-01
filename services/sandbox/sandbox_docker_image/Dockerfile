FROM alpine:3.14.0

LABEL maintainer="Andrew Gein <andgein@hackerdom.ru>"

RUN apk add --no-cache gcc musl-dev

RUN find /bin /usr/bin ! -name 'gcc' ! -name 'sh' ! -name 'busybox' ! -name 'rm' -type f -exec rm -f {} +

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
