import hashlib
import random
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, insert, update, and_

import database


async def find_program_by_id(program_id: int) -> Optional[database.Program]:
    query = select([database.Program]).where(database.Program.id == program_id)
    return database.Program.from_database(await database.db.fetch_one(query))


async def get_user_programs(user_id: int) -> list[database.Program]:
    query = select([database.Program]).where(database.Program.user_id == user_id)
    return [database.Program.from_database(row) for row in await database.db.fetch_all(query)]


async def create_program(user_id: int, code: str) -> database.Program:
    query = insert(database.Program).values(user_id=user_id, code=code)
    program_id = await database.db.execute(query)
    return await find_program_by_id(program_id)


async def find_challenge_by_id(challenge_id: int) -> Optional[database.ProofOfWorkChallenge]:
    query = select([database.ProofOfWorkChallenge]).where(database.ProofOfWorkChallenge.id == challenge_id)
    return database.ProofOfWorkChallenge.from_database(await database.db.fetch_one(query))


async def get_challenges_for_last_minute(program_id: int) -> list[database.ProofOfWorkChallenge]:
    since = datetime.now() - timedelta(minutes=1)
    query = select([database.ProofOfWorkChallenge]).where(
        and_(database.ProofOfWorkChallenge.program_id == program_id, database.ProofOfWorkChallenge.create_time >= since)
    )
    return [database.ProofOfWorkChallenge.from_database(row) for row in await database.db.fetch_all(query)]


challenges: dict[int, int] = {}
MIN_CHALLENGE = 0
MAX_CHALLENGE = 99999


def generate_proof_of_work_challenge() -> int:
    timestamp = int(datetime.now().timestamp())
    key = timestamp // 10
    if key not in challenges:
        challenges[key] = random.randint(MIN_CHALLENGE, MAX_CHALLENGE)
    return challenges[key]


async def create_proof_of_work_challenge(program_id: int, prefix: int) -> database.ProofOfWorkChallenge:
    query = insert(database.ProofOfWorkChallenge).values(
        program_id=program_id, prefix=prefix, is_used=False, create_time=datetime.now()
    )
    challenge_id = await database.db.execute(query)
    return await find_challenge_by_id(challenge_id)


def check_challenge_response(challenge: database.ProofOfWorkChallenge, challenge_response: str) -> bool:
    return hashlib.sha256(f"{challenge.prefix:08x}{challenge_response}".encode()).hexdigest().startswith("000000")


async def mark_challenge_as_used(challenge_id: int):
    query = update(database.ProofOfWorkChallenge).where(database.ProofOfWorkChallenge.id == challenge_id).values(is_used=True)
    await database.db.execute(query)