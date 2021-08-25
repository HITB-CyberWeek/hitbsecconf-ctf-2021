import hashlib
import pathlib
import string
import tempfile
import uuid

import asyncssh
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette import status

import database
import models
import programs
import sandbox
import settings
import users

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> database.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = await users.find_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user


@app.on_event("startup")
async def startup():
    await sandbox.upload_sandbox_docker_image()
    await database.db.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.db.disconnect()


@app.get("/", include_in_schema=False, response_model=models.IndexResponse)
def index() -> models.IndexResponse:
    return models.IndexResponse(
        welcome="Welcome to the Sandbox API. "
                "This service has no frontend: only API, only hardcode. "
                "You can observe an API and play with it on /docs."
    )


@app.post(
    "/users",
    response_model=models.UserResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "User with same username already exists"
        }
    },
    tags=["users"],
)
async def create_user(request: models.CreateUserRequest) -> models.UserResponse:
    try:
        created_user = await users.create_user(request.username, request.password)
    except users.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with same username already exists",
        )
    return models.UserResponse(user=models.User.from_orm(created_user))


@app.post(
    "/login",
    response_model=models.TokenResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Invalid username or password"
        }
    },
    tags=["users"],
)
async def login(form: OAuth2PasswordRequestForm = Depends()) -> models.TokenResponse:
    user = await users.find_user_by_username(form.username)
    if not user or not users.verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid username or password",
        )
    access_token = users.create_access_token({"sub": str(user.id)})
    return models.TokenResponse(access_token=access_token, token_type="bearer")


@app.get(
    "/programs",
    response_model=models.ProgramListResponse,
    tags=["programs"],
)
async def list_programs(user: database.User = Depends(get_current_user)) -> models.ProgramListResponse:
    user_programs = await programs.get_user_programs(user.id)
    return models.ProgramListResponse(programs=[models.Program.from_orm(user_program) for user_program in user_programs])


@app.post(
    "/programs",
    response_model=models.ProgramResponse,
    tags=["programs"],
)
async def create_program(request: models.CreateProgramRequest, user: database.User = Depends(get_current_user)) -> models.ProgramResponse:
    created_program = await programs.create_program(user.id, request.code)
    return models.ProgramResponse(program=models.Program.from_orm(created_program))


@app.post(
    "/programs/{program_id}/challenge",
    response_model=models.ProofOfWorkChallengeResponse,
    tags=["programs"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Program not found",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "You are not allowed to get challenges for other's programs",
        },
        status.HTTP_425_TOO_EARLY: {
            "description": "Too fast. You can not request more than 5 challenges in a minute"
        },
    }
)
async def get_proof_of_work_challenge(program_id: int, user: database.User = Depends(get_current_user)) -> models.ProofOfWorkChallengeResponse:
    program = await programs.find_program_by_id(program_id)
    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program {program_id} not found",
        )
    if program.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to run other's programs",
        )

    if len(await programs.get_challenges_for_last_minute(program_id)) > 5:
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="Too fast. You can not request more than 5 challenges in a minute"
        )

    prefix = programs.generate_proof_of_work_challenge()
    challenge = await programs.create_proof_of_work_challenge(program_id, prefix)
    return models.ProofOfWorkChallengeResponse(
        challenge_id=challenge.id,
        prefix=f"{prefix:08x}",
        task="To run a program you should do some work. "
             f"Please find any 8-digit hexadecimal SUFFIX such that sha256_hexdigest('{prefix:08x}<SUFFIX>') "
             "starts with '000000'."
    )


@app.post(
    "/programs/{program_id}/run",
    response_model=models.RunProgramResponse,
    tags=["programs"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Program not found",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "You are not allowed to run other's programs or invalid response for proof-of-work challenge",
        },
    }
)
async def run_program(program_id: int, request: models.RunProgramRequest, user: database.User = Depends(get_current_user)) -> models.RunProgramResponse:
    program = await programs.find_program_by_id(program_id)
    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program {program_id} not found",
        )
    if program.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to run other's programs",
        )

    challenge = await programs.find_challenge_by_id(request.challenge_id)
    if challenge is None or challenge.program_id != program_id or challenge.is_used:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid challenge id"
        )

    if len(request.challenge_response) != 8 or not all(c in string.hexdigits for c in request.challenge_response):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid challenge response, should be 8-digit hexadecimal string"
        )

    if not programs.check_challenge_response(challenge, request.challenge_response):
        h = hashlib.sha256(f"{challenge.prefix:08x}{request.challenge_response}".encode()).hexdigest()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid challenge response: "
                   f"sha256_hexdigest('{challenge.prefix:08x}{request.challenge_response}') = {h}. "
                   f"Should start with '000000', not with '{h[:6]}'."
        )

    working_directory = f"/tmp/{uuid.uuid4()}"
    async with asyncssh.connect(
            settings.DOCKER_HOST,
            username=settings.SSH_USERNAME,
            client_keys=[settings.SSH_KEY_PATH.as_posix()],
            known_hosts=None
    ) as ssh_connection:
        await ssh_connection.run(f"mkdir {working_directory}")
        sftp_connection = await ssh_connection.start_sftp_client()

        await upload_file_to_server(sftp_connection, program.code, f"{working_directory}/program.c")
        await upload_file_to_server(sftp_connection, request.input, f"{working_directory}/input")

        log = await sandbox.run_sandbox_docker_container(working_directory)

        output = await download_file_from_server(sftp_connection, f"{working_directory}/output")
        await ssh_connection.run(f"rm -rf {working_directory}")

    return models.RunProgramResponse(
        log=log,
        output=output,
    )


async def upload_file_to_server(sftp_connection: asyncssh.SFTPClient, data: str, remote_path: str):
    with tempfile.NamedTemporaryFile(mode="w", prefix="upload-") as upload_file:
        upload_file.write(data)
        upload_file.flush()
        await sftp_connection.put(upload_file.name, remote_path)


async def download_file_from_server(sftp_connection: asyncssh.SFTPClient, remote_path: str) -> str:
    with tempfile.NamedTemporaryFile(prefix="download-") as download_file:
        try:
            await sftp_connection.get(remote_path, download_file.name)
        except asyncssh.sftp.SFTPNoSuchFile:
            return ""
        return pathlib.Path(download_file.name).read_text()


if __name__ == '__main__':
    uvicorn.run("app:app", host=settings.HOST, port=settings.PORT, reload=True)
