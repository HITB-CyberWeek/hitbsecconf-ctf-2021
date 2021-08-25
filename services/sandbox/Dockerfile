FROM python:3.9-slim

LABEL maintainer="Andrew Gein <andgein@hackerdom.ru>"

RUN pip install --no-cache-dir "uvicorn[standard]" gunicorn

COPY src/requirements.txt /
RUN pip install --no-cache-dir -Ur /requirements.txt

COPY src /app
WORKDIR /app/

COPY sandbox_docker_image/sandbox.tar.gz /
COPY ./keys /keys

ENV DOCKER_SANDBOX_IMAGE_PATH=../sandbox.tar.gz
ENV PYTHONPATH=/app

CMD ["/app/entrypoint.sh"]
