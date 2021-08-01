from typing import Literal

from pydantic import BaseModel, constr


class SuccessResponse(BaseModel):
    status: Literal["ok"] = "ok"


class CreateUserRequest(BaseModel):
    username: constr(min_length=1, max_length=50)
    password: str


class CreateProgramRequest(BaseModel):
    code: str


class RunProgramRequest(BaseModel):
    input: str


class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class Program(BaseModel):
    id: int
    code: str

    class Config:
        orm_mode = True


class IndexResponse(SuccessResponse):
    welcome: str


class UserResponse(SuccessResponse):
    user: User


class TokenResponse(SuccessResponse):
    access_token: str
    token_type: str


class ProgramListResponse(SuccessResponse):
    programs: list[Program]


class ProgramResponse(SuccessResponse):
    program: Program


class RunProgramResponse(SuccessResponse):
    log: str
    output: str
