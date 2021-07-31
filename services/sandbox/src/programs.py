from typing import Optional

from sqlalchemy import select, insert

import database


async def get_program_by_id(program_id: int) -> Optional[database.Program]:
    query = select([database.Program]).where(database.Program.id == program_id)
    return database.Program.from_database(await database.db.fetch_one(query))


async def get_user_programs(user_id: int) -> list[database.Program]:
    query = select([database.Program]).where(database.Program.user_id == user_id)
    return [database.Program.from_database(row) for row in await database.db.fetch_all(query)]


async def create_program(user_id: int, code: str) -> database.Program:
    query = insert(database.Program).values(user_id=user_id, code=code)
    program_id = await database.db.execute(query)
    return await get_program_by_id(program_id)
