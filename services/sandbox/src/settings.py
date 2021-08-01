import pathlib

BASE_DIR = pathlib.Path(__file__).parent

DATABASE_URL = "sqlite:///./db.sqlite"
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

JWT_SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e8"
JWT_ALGORITHM = "HS256"

DOCKER_HOST = "docker.sandbox.2021.ctf.hitb.org"
DOCKER_URL = f"https://{DOCKER_HOST}:2376"
DOCKER_CERTIFICATES_PATH = BASE_DIR.parent / "certificates"
