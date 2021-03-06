from typing import Optional

import databases
import sqlalchemy
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import settings

db = databases.Database(settings.DATABASE_URL)

engine = sqlalchemy.create_engine(settings.DATABASE_URL, connect_args=settings.DATABASE_CONNECTION_OPTIONS)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=50), unique=True, index=True)
    hashed_password = Column(String(length=72))

    programs = relationship("Program")

    @staticmethod
    def from_database(data) -> Optional["User"]:
        if data is None:
            return None
        return User(**data)


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), index=True)
    user = relationship(User, back_populates="programs")
    code = Column(Text)

    @staticmethod
    def from_database(data) -> Optional["Program"]:
        if data is None:
            return None
        return Program(**data)


class ProofOfWorkChallenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    program_id = Column(Integer, ForeignKey(Program.id), index=True)
    prefix = Column(Integer)
    is_used = Column(Boolean)
    create_time = Column(DateTime)

    @staticmethod
    def from_database(data) -> Optional["ProofOfWorkChallenge"]:
        if data is None:
            return None
        return ProofOfWorkChallenge(**data)


if settings.AUTO_MIGRATE_DATABASE:
    Base.metadata.create_all(engine)
