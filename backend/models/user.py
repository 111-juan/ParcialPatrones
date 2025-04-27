from sqlalchemy import JSON, Column, Integer, String
from sqlmodel import Field, Relationship, SQLModel
from pydantic import BaseModel


class User(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, autoincrement=True,
                         primary_key=True, index=True),
    )
    name: str = Field(index=True)
    cedula: str = Field(sa_column=Column(String, unique=True, nullable=False))
    email: str = Field(sa_column=Column(String, unique=True, nullable=False))
    birthdate: str = Field(sa_column=Column(String, nullable=False))
    roles: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class UserAuth(SQLModel, table=True):
    id: int = Field(
        default=None,
        sa_column=Column(Integer, autoincrement=True,
                         primary_key=True, index=True),
    )
    email: str = Field(
        sa_column=Column(String, unique=True, nullable=False, index=True)
    )
    password: str = Field()
    user_id: int = Field(foreign_key="user.id")


User.auth = Relationship(back_populates="user")
UserAuth.user = Relationship(back_populates="auth")


class UserCreate(BaseModel):
    name: str
    cedula: str
    email: str
    birthdate: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str
