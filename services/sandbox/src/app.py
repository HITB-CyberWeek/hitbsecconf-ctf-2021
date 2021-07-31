import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette import status

import database
import models
import programs
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
    await database.db.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.db.disconnect()


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


if __name__ == '__main__':
    uvicorn.run("app:app", reload=True)
