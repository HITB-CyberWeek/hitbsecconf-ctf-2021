from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select, insert

import database
import settings

password_crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserAlreadyExists(Exception):
    pass


async def find_user_by_username(username: str) -> Optional[database.User]:
    query = select([database.User]).where(database.User.username == username)
    return database.User.from_database(await database.db.fetch_one(query))


async def find_user_by_id(user_id: int) -> Optional[database.User]:
    query = select([database.User]).where(database.User.id == user_id)
    return database.User.from_database(await database.db.fetch_one(query))


def get_password_hash(password: str) -> str:
    return password_crypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_crypt_context.verify(plain_password, hashed_password)


async def create_user(username: str, password: str) -> database.User:
    existing_user = await find_user_by_username(username)

    if existing_user is not None:
        raise UserAlreadyExists()

    hashed_password = get_password_hash(password)
    query = insert(database.User).values(username=username, hashed_password=hashed_password)
    user_id = await database.db.execute(query)

    return await find_user_by_id(user_id)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=500)

    to_encode = {**data, "exp": datetime.utcnow() + expires_delta}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
