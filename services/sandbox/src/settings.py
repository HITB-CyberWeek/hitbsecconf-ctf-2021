import json
import pathlib
import random
import string

from environs import Env


def read_or_generate_jwt_token() -> str:
    jwt_token_path = pathlib.Path("jwt.token")
    if jwt_token_path.exists():
        return jwt_token_path.read_text().strip()

    new_jwt_token = "".join(random.choice(string.hexdigits) for _ in range(64))
    jwt_token_path.write_text(new_jwt_token)
    return new_jwt_token


env = Env()
env.read_env()  # read .env file, if it exists

BASE_DIR = pathlib.Path(__file__).parent

HOST = env.str("HOST", "127.0.0.1")
PORT = env.int("PORT", 8000)

AUTO_MIGRATE_DATABASE = env.bool("AUTO_MIGRATE_DATABASE", True)

DATABASE_URL = env.str("DATABASE_URL", "sqlite:///./db.sqlite")
DATABASE_CONNECTION_OPTIONS = env.json("DATABASE_CONNECTION_OPTIONS", json.dumps({"check_same_thread": False}))

JWT_SECRET = env.str("JWT_SECRET", read_or_generate_jwt_token())
JWT_ALGORITHM = env.str("JWT_ALGORITHM", "HS256")

DOCKER_HOST = env.str("DOCKER_HOST", "docker.sandbox.2021.ctf.hitb.org")
DOCKER_URL = f"tcp://{DOCKER_HOST}:2375"

SSH_USERNAME = env.str("SSH_USERNAME", "sandbox")
SSH_KEY_PATH = env.path("SSH_KEY_PATH", str(BASE_DIR.parent / "keys" / "id_rsa"))

DOCKER_SANDBOX_IMAGE_PATH = env.path("DOCKER_SANDBOX_IMAGE_PATH", str(BASE_DIR.parent / "sandbox_docker_image" / "sandbox.tar.gz"))
