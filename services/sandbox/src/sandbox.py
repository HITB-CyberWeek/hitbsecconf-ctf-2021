import asyncio
import ssl
from typing import Any

import aiodocker
import aiohttp

import settings


def create_docker_ssl_context() -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    certs = settings.DOCKER_CERTIFICATES_PATH
    context.load_verify_locations(cafile=(certs / "ca.pem").as_posix())
    context.load_cert_chain(
        certfile=(certs / "docker.pem").as_posix(), keyfile=(certs / "docker.key.pem").as_posix()
    )
    return context


def create_docker_connection() -> aiodocker.Docker:
    ssl_context = create_docker_ssl_context()
    return aiodocker.Docker(url=settings.DOCKER_URL, connector=aiohttp.TCPConnector(ssl=ssl_context))


def get_docker_container_config(working_directory: str) -> dict[str, Any]:
    return {
        "Cmd": [],
        "Image": "sandbox",
        "AttachStdin": False,
        "AttachStdout": False,
        "AttachStderr": False,
        "Tty": False,
        "OpenStdin": False,
        "StopTimeout": 1,
        "HostConfig": {
            "Memory": 10 * 1024 * 1024,
            "NanoCpus": 100_000_000,
            "ReadonlyRootfs": True,
            "Mounts": [
                {
                    "Type": "bind",
                    "Source": working_directory,
                    "Target": "/work",
                }
            ],
        },
    }


async def run_sandbox_docker_container(working_directory: str) -> str:
    async with create_docker_connection() as docker:
        config = get_docker_container_config(working_directory)
        container = await docker.containers.run(config=config)
        try:
            try:
                await container.wait(timeout=5)
            except asyncio.TimeoutError:
                await container.stop()

            return "".join(await container.log(stdout=True, stderr=True))
        finally:
            await container.delete()


async def upload_sandbox_docker_image():
    async with create_docker_connection() as docker:
        await docker.images.import_image(settings.DOCKER_SANDBOX_IMAGE_PATH.read_bytes())
