from typing import Literal, Type, Any

from pydantic import BaseModel, constr


class SuccessResponse(BaseModel):
    status: Literal["ok"] = "ok"


class CreateUserRequest(BaseModel):
    username: constr(min_length=1, max_length=50)
    password: str


class CreateProgramRequest(BaseModel):
    code: constr(max_length=10000)


class RunProgramRequest(BaseModel):
    challenge_id: int
    challenge_response: str
    input: constr(max_length=10000)


class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class Program(BaseModel):
    id: int
    code_prefix: constr(max_length=50)

    @classmethod
    def from_orm(cls: Type["Program"], orm_program: Any) -> "Program":
        return cls(id=orm_program.id, code_prefix=orm_program.code[:50])


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


class ProofOfWorkChallengeResponse(SuccessResponse):
    challenge_id: int
    prefix: str
    task: str
