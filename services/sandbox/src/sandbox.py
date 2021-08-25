import asyncio
from typing import Any

import aiodocker

import settings


def create_docker_connection() -> aiodocker.Docker:
    return aiodocker.Docker(url=settings.DOCKER_URL)


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
