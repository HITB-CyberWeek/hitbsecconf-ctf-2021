import settings

# Gunicorn config variables
loglevel = "info"
workers = 4
bind = f"{settings.HOST}:{settings.PORT}"
errorlog = "-"
worker_tmp_dir = "/dev/shm"
accesslog = "-"
graceful_timeout = 120
timeout = 120
keepalive = 5