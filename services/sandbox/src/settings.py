import json
import pathlib
from environs import Env

env = Env()
env.read_env()  # read .env file, if it exists

BASE_DIR = pathlib.Path(__file__).parent

HOST = env.str("HOST", "127.0.0.1")
PORT = env.int("PORT", 8000)

AUTO_MIGRATE_DATABASE = env.bool("AUTO_MIGRATE_DATABASE", True)

DATABASE_URL = env.str("DATABASE_URL", "sqlite:///./db.sqlite")
DATABASE_CONNECTION_OPTIONS = env.json("DATABASE_CONNECTION_OPTIONS", json.dumps({"check_same_thread": False}))

JWT_SECRET = env.str("JWT_SECRET", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e8")
JWT_ALGORITHM = env.str("JWT_ALGORITHM", "HS256")

DOCKER_HOST = env.str("DOCKER_HOST", "docker.sandbox.2021.ctf.hitb.org")
DOCKER_URL = f"tcp://{DOCKER_HOST}:2376"

SSH_USERNAME = env.str("SSH_USERNAME", "sandbox")
SSH_KEY_PATH = env.path("SSH_KEY_PATH", str(BASE_DIR.parent / "keys" / "id_rsa"))

DOCKER_SANDBOX_IMAGE_PATH = env.path("DOCKER_SANDBOX_IMAGE_PATH", str(BASE_DIR.parent / "sandbox_docker_image" / "sandbox.tar.gz"))
